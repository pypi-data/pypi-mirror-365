"""
Application service for async task management

This service handles the submit/barrier pattern for asynchronous image generation,
managing task lifecycle and result collection.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional

from ..domain.entities import AsyncTask, TaskStatus, ConversationType
from ..domain.services.conversation_service import ConversationService
from .image_service import ImageGenerationService

logger = logging.getLogger(__name__)


class TaskManagementService:
    """Service for managing asynchronous tasks with submit/barrier pattern"""

    def __init__(
        self,
        image_service: ImageGenerationService,
        conversation_service: ConversationService,
    ):
        self.image_service = image_service
        self.conversation_service = conversation_service
        self._lock = asyncio.Lock()

        # Task storage - no LRU, tasks managed through conversation lifecycle
        self.executing_tasks: Dict[str, AsyncTask] = {}  # task_id -> AsyncTask
        self.completed_tasks: Dict[
            str, AsyncTask
        ] = {}  # task_id -> AsyncTask (for barrier collection)
        self.asyncio_tasks: Dict[str, asyncio.Task] = {}  # task_id -> asyncio.Task

        logger.info("TaskManagementService initialized with conversation integration")

    async def submit_gpt_image_task(
        self,
        prompt: str,
        output_path: str,
        conversation_id: Optional[str] = None,
        quality: str = "auto",
        size: str = "auto",
        format: str = "png",
        background: str = "opaque",
        output_compression: Optional[int] = None,
        input_image: Optional[str] = None,
    ) -> str:
        """
        Submit a GPT image generation task for async execution

        Args:
            prompt: Image generation prompt
            output_path: Path where to save the generated image
            conversation_id: Required conversation ID
            quality: Image quality setting
            size: Image size setting
            format: Output format
            background: Background type
            output_compression: Compression level
            input_image: Base64 encoded reference image

        Returns:
            Task ID for tracking
        """
        # Generate conversation ID if not provided
        if conversation_id is None:
            conversation_id = f"gpt_task_{int(time.time())}"

        # Create task through conversation service to get proper sequential ID
        task_id = self.conversation_service.create_task_for_conversation(
            conversation_id=conversation_id,
            conversation_type=ConversationType.IMAGE,
            task_type="gpt_image",
        )

        # Create task entity with proper relationship
        task = AsyncTask(
            task_id=task_id,
            conversation_id=conversation_id,
            task_sequence=int(task_id.split("_task_")[1]),
            task_type="gpt_image",
        )

        # Create coroutine for execution
        coro = self._execute_gpt_image_task(
            task=task,
            prompt=prompt,
            output_path=output_path,
            quality=quality,
            size=size,
            format=format,
            background=background,
            output_compression=output_compression,
            input_image=input_image,
        )

        # Submit for execution
        async with self._lock:
            task.mark_executing()
            self.executing_tasks[task_id] = task

            # Create and start asyncio task
            asyncio_task = asyncio.create_task(coro)
            self.asyncio_tasks[task_id] = asyncio_task

            logger.info(f"GPT image task {task_id} submitted and started execution")

        return task_id

    async def submit_flux_image_task(
        self,
        prompt: str,
        output_path: str,
        conversation_id: Optional[str] = None,
        aspect_ratio: str = "1:1",
        output_format: str = "png",
        seed: Optional[int] = None,
        input_image: Optional[str] = None,
    ) -> str:
        """
        Submit a FLUX image generation task for async execution

        Args:
            prompt: Image generation prompt
            output_path: Path where to save the generated image
            conversation_id: Required conversation ID
            aspect_ratio: Image aspect ratio
            output_format: Output format
            seed: Optional seed for reproducible generation
            input_image: Base64 encoded reference image

        Returns:
            Task ID for tracking
        """
        # Generate conversation ID if not provided
        if conversation_id is None:
            conversation_id = f"flux_task_{int(time.time())}"

        # Create task through conversation service to get proper sequential ID
        task_id = self.conversation_service.create_task_for_conversation(
            conversation_id=conversation_id,
            conversation_type=ConversationType.FLUX,
            task_type="flux_image",
        )

        # Create task entity with proper relationship
        task = AsyncTask(
            task_id=task_id,
            conversation_id=conversation_id,
            task_sequence=int(task_id.split("_task_")[1]),
            task_type="flux_image",
        )

        # Create coroutine for execution
        coro = self._execute_flux_image_task(
            task=task,
            prompt=prompt,
            output_path=output_path,
            aspect_ratio=aspect_ratio,
            output_format=output_format,
            seed=seed,
            input_image=input_image,
        )

        # Submit for execution
        async with self._lock:
            task.mark_executing()
            self.executing_tasks[task_id] = task

            # Create and start asyncio task
            asyncio_task = asyncio.create_task(coro)
            self.asyncio_tasks[task_id] = asyncio_task

            logger.info(f"FLUX image task {task_id} submitted and started execution")

        return task_id

    async def wait_for_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """
        Wait for all executing tasks to complete and return results (barrier)

        Returns:
            Dictionary mapping task_ids to their results/status
        """
        # Get snapshot of currently executing tasks
        async with self._lock:
            executing_tasks_snapshot = dict(self.asyncio_tasks)
            logger.info(f"Waiting for {len(executing_tasks_snapshot)} executing tasks")

        # Wait for all executing tasks to complete
        if executing_tasks_snapshot:
            try:
                # Wait for all tasks with a reasonable timeout
                await asyncio.wait_for(
                    asyncio.gather(
                        *executing_tasks_snapshot.values(), return_exceptions=True
                    ),
                    timeout=600,  # 10 minutes total timeout
                )
                logger.info("All executing tasks completed")
            except asyncio.TimeoutError:
                logger.warning("Some tasks timed out during barrier wait")

        # Collect all results from completed tasks
        async with self._lock:
            results = {}
            completed_count = 0
            failed_count = 0

            # Process all completed tasks and collect their results
            for task_id, task in self.completed_tasks.items():
                try:
                    if task.status == TaskStatus.COMPLETED:
                        results[task_id] = {
                            "success": True,
                            "output_path": task.result.get("output_path")
                            if task.result
                            else None,
                            "error": None,
                            "conversation_id": task.conversation_id,
                        }
                        completed_count += 1
                    elif task.status == TaskStatus.FAILED:
                        results[task_id] = {
                            "success": False,
                            "output_path": None,
                            "error": task.error_message,
                            "conversation_id": task.conversation_id,
                        }
                        failed_count += 1
                    elif task.status in [TaskStatus.PENDING, TaskStatus.EXECUTING]:
                        # Task is still running, mark as failed for now
                        results[task_id] = {
                            "success": False,
                            "output_path": None,
                            "error": f"Task still in {task.status.value} state",
                            "conversation_id": task.conversation_id,
                        }
                        failed_count += 1
                except Exception as e:
                    results[task_id] = {
                        "success": False,
                        "output_path": None,
                        "error": f"Error collecting result: {str(e)}",
                        "conversation_id": getattr(task, "conversation_id", "unknown"),
                    }
                    failed_count += 1

            logger.info(
                f"Barrier completed - {completed_count} succeeded, {failed_count} failed"
            )

            # Clear completed tasks after collecting results
            self.completed_tasks.clear()

            # Return summary
            return {
                "completed": completed_count,
                "failed": failed_count,
                "total": completed_count + failed_count,
                "results": results,
            }

    async def get_task_status(self) -> Dict[str, Any]:
        """Get current task manager status"""
        async with self._lock:
            return {
                "executing_tasks": len(self.executing_tasks),
                "executing_task_ids": list(self.executing_tasks.keys()),
            }

    async def _execute_gpt_image_task(
        self, task: AsyncTask, prompt: str, output_path: str, **kwargs
    ) -> None:
        """Execute GPT image generation task"""
        try:
            # Generate image using service
            image = await self.image_service.generate_gpt_image_async(
                prompt=prompt, output_path=output_path, **kwargs
            )

            # Create result
            result = {
                "image_id": image.image_id,
                "prompt": image.prompt,
                "image_urls": image.image_urls,
                "local_paths": image.local_paths,
                "model_used": image.model_used,
                "provider_name": image.provider_name,
                "output_path": output_path,
            }

            # Mark task as completed and move to completed tasks
            async with self._lock:
                task.mark_completed(result)
                if task.task_id in self.executing_tasks:
                    del self.executing_tasks[task.task_id]
                self.completed_tasks[task.task_id] = task

            # Notify conversation service that task is completed
            self.conversation_service.mark_task_completed(
                task_id=task.task_id,
                conversation_id=task.conversation_id,
                conversation_type=ConversationType.IMAGE,
            )

        except Exception as e:
            # Mark task as failed and move to completed tasks
            async with self._lock:
                task.mark_failed(str(e))
                if task.task_id in self.executing_tasks:
                    del self.executing_tasks[task.task_id]
                self.completed_tasks[task.task_id] = task

            # Notify conversation service that task is completed (even if failed)
            self.conversation_service.mark_task_completed(
                task_id=task.task_id,
                conversation_id=task.conversation_id,
                conversation_type=ConversationType.IMAGE,
            )

    async def _execute_flux_image_task(
        self, task: AsyncTask, prompt: str, output_path: str, **kwargs
    ) -> None:
        """Execute FLUX image generation task"""
        try:
            # Generate image using service
            image = await self.image_service.generate_flux_image_async(
                prompt=prompt, output_path=output_path, **kwargs
            )

            # Create result
            result = {
                "image_id": image.image_id,
                "prompt": image.prompt,
                "image_urls": image.image_urls,
                "local_paths": image.local_paths,
                "model_used": image.model_used,
                "provider_name": image.provider_name,
                "output_path": output_path,
            }

            # Mark task as completed and move to completed tasks
            async with self._lock:
                task.mark_completed(result)
                if task.task_id in self.executing_tasks:
                    del self.executing_tasks[task.task_id]
                self.completed_tasks[task.task_id] = task

            # Notify conversation service that task is completed
            self.conversation_service.mark_task_completed(
                task_id=task.task_id,
                conversation_id=task.conversation_id,
                conversation_type=ConversationType.FLUX,
            )

        except Exception as e:
            # Mark task as failed and move to completed tasks
            async with self._lock:
                task.mark_failed(str(e))
                if task.task_id in self.executing_tasks:
                    del self.executing_tasks[task.task_id]
                self.completed_tasks[task.task_id] = task

            # Notify conversation service that task is completed (even if failed)
            self.conversation_service.mark_task_completed(
                task_id=task.task_id,
                conversation_id=task.conversation_id,
                conversation_type=ConversationType.FLUX,
            )

    def _remove_from_executing(self, task: AsyncTask) -> None:
        """Remove task from executing lists (must be called with lock held)"""
        task_id = task.task_id

        # Remove from executing
        if task_id in self.executing_tasks:
            del self.executing_tasks[task_id]
        if task_id in self.asyncio_tasks:
            del self.asyncio_tasks[task_id]

        logger.info(
            f"Task {task_id} removed from executing with status: {task.status.value}"
        )
