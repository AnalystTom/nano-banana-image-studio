import os
import json
import aiosqlite
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

# Check for Anthropic library availability
try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from ..database import DATABASE_PATH

# Get API key from environment
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

# System prompts
SCRIPT_GENERATION_SYSTEM_PROMPT = """You are an expert video script writer specializing in short-form content.
Create a detailed script broken down into logical scenes based on the user's narrative.

For each scene, specify:
- Scene description and action
- Visual elements and composition
- Mood and tone
- Approximate duration

The script should be optimized for AI-generated video with clear visual descriptions.
Use markdown formatting with ## Scene N headers for each scene."""

SCENE_BREAKDOWN_SYSTEM_PROMPT = """You are a visual storytelling expert. Break down the provided script into structured scenes suitable for video generation.

For each scene, provide:
1. Scene number and description
2. Opening frame description (detailed image prompt for the first frame)
3. Closing frame description (detailed image prompt for the last frame, if different from opening)
4. Camera direction/movement (static, pan-left, pan-right, zoom-in, zoom-out, tilt-up, tilt-down)
5. Duration in seconds

Ensure visual continuity between scenes for characters, lighting, and style.
Output ONLY a valid JSON array with no additional text. Each scene object must have these exact keys:
{
  "scene_number": int,
  "description": str,
  "opening_frame_prompt": str,
  "closing_frame_prompt": str or null,
  "camera_direction": str,
  "duration": float
}"""

PROMPT_REFINEMENT_SYSTEM_PROMPT = """You are an expert at refining image and video generation prompts.
Given an original prompt and user feedback, create an improved version that incorporates the feedback while maintaining the core intent."""

CONSISTENCY_CHECK_SYSTEM_PROMPT = """You are a visual continuity expert. Review the provided scenes and ensure consistency in:
- Character descriptions (if any)
- Lighting conditions
- Color palette
- Visual style
- Setting details

Return the scenes with any necessary adjustments to maintain visual coherence.
Output ONLY a valid JSON array matching the input structure."""


class ClaudeService:
    """Service for Claude API integration in video production workflow."""
    
    @staticmethod
    def generate_mock_script(narrative: str, style: str, target_duration: int) -> str:
        """Generate a mock script for development/testing."""
        scene_count = max(3, target_duration // 10)  # ~10s per scene
        
        script = f"# Video Script: {narrative[:50]}\n\n"
        script += f"**Style**: {style}\n"
        script += f"**Duration**: ~{target_duration} seconds\n\n"
        
        for i in range(scene_count):
            scene_start = i * (target_duration // scene_count)
            scene_end = (i + 1) * (target_duration // scene_count)
            script += f"## Scene {i+1} ({scene_start}-{scene_end}s)\n\n"
            script += f"**Description**: Scene {i+1} of {narrative}\n\n"
            script += f"**Visual**: {style.capitalize()} style imagery with dramatic composition\n\n"
            script += f"**Action**: Progressive story development showing {narrative}\n\n"
            script += f"**Mood**: {style.capitalize()} and engaging\n\n"
        
        return script
    
    @staticmethod
    def generate_mock_scenes(script_content: str, target_duration: int, style: str) -> List[Dict[str, Any]]:
        """Generate mock scene breakdown for development/testing."""
        # Count scenes in script
        scene_pattern = r'##\s*Scene\s+(\d+)'
        matches = re.findall(scene_pattern, script_content)
        scene_count = len(matches) if matches else 3
        
        scenes = []
        duration_per_scene = target_duration / scene_count
        
        for i in range(scene_count):
            scenes.append({
                "scene_number": i + 1,
                "description": f"Scene {i+1} from the script with {style} styling",
                "opening_frame_prompt": f"A {style} style opening shot for scene {i+1}, cinematic composition, professional lighting",
                "closing_frame_prompt": f"A {style} style closing shot for scene {i+1}, smooth transition ready" if i < scene_count - 1 else None,
                "camera_direction": ["static", "pan-left", "pan-right", "zoom-in"][i % 4],
                "duration": round(duration_per_scene, 1)
            })
        
        return scenes
    
    @staticmethod
    async def generate_script(
        project_id: str,
        narrative: str,
        style: str,
        target_duration: int,
        aspect_ratio: str
    ) -> Dict[str, Any]:
        """Generate a video script from narrative using Claude.
        
        Args:
            project_id: Project ID for logging
            narrative: User's story/concept
            style: Visual style (cinematic, minimal, vibrant, dark)
            target_duration: Target video length in seconds
            aspect_ratio: Video aspect ratio
            
        Returns:
            Dict with keys: content (str), scene_count (int), token_count (int), is_mock (bool)
        """
        # Check if API key is available
        if not ANTHROPIC_API_KEY or not ANTHROPIC_AVAILABLE:
            # Use mock mode
            script_content = ClaudeService.generate_mock_script(narrative, style, target_duration)
            scene_count = len(re.findall(r'##\s*Scene\s+\d+', script_content))
            
            await ClaudeService._log_interaction(
                project_id=project_id,
                phase="script_generation",
                user_message=f"Narrative: {narrative}",
                claude_response=script_content[:500] + "...",
                token_count=0,
                model="mock"
            )
            
            return {
                "content": script_content,
                "scene_count": scene_count,
                "token_count": 0,
                "is_mock": True
            }
        
        # Use Claude API
        try:
            client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
            
            user_prompt = f"""Create a video script for the following concept:

Narrative: {narrative}
Style: {style}
Target Duration: {target_duration} seconds
Aspect Ratio: {aspect_ratio}

Break the script into approximately {max(3, target_duration // 10)} scenes.
Each scene should be clearly marked with "## Scene N" headers.
Provide rich visual descriptions suitable for AI video generation."""

            message = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                system=SCRIPT_GENERATION_SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )
            
            script_content = message.content[0].text
            scene_count = len(re.findall(r'##\s*Scene\s+\d+', script_content))
            token_count = message.usage.input_tokens + message.usage.output_tokens
            
            # Log interaction
            await ClaudeService._log_interaction(
                project_id=project_id,
                phase="script_generation",
                user_message=user_prompt,
                claude_response=script_content,
                token_count=token_count,
                model="claude-3-5-sonnet-20241022"
            )
            
            return {
                "content": script_content,
                "scene_count": scene_count,
                "token_count": token_count,
                "is_mock": False
            }
            
        except Exception as e:
            # Fall back to mock on error
            print(f"Claude API error: {e}, falling back to mock")
            script_content = ClaudeService.generate_mock_script(narrative, style, target_duration)
            scene_count = len(re.findall(r'##\s*Scene\s+\d+', script_content))
            
            return {
                "content": script_content,
                "scene_count": scene_count,
                "token_count": 0,
                "is_mock": True,
                "error": str(e)
            }
    
    @staticmethod
    async def breakdown_into_scenes(
        project_id: str,
        script_content: str,
        target_duration: int,
        style: str
    ) -> List[Dict[str, Any]]:
        """Break script into structured scenes with frame descriptions.
        
        Returns list of scenes, each with:
        - scene_number: int
        - description: str
        - opening_frame_prompt: str
        - closing_frame_prompt: str (optional)
        - camera_direction: str
        - duration: float
        """
        # Check if API key is available
        if not ANTHROPIC_API_KEY or not ANTHROPIC_AVAILABLE:
            # Use mock mode
            scenes = ClaudeService.generate_mock_scenes(script_content, target_duration, style)
            
            await ClaudeService._log_interaction(
                project_id=project_id,
                phase="scene_breakdown",
                user_message="Script breakdown request",
                claude_response=json.dumps(scenes, indent=2),
                token_count=0,
                model="mock"
            )
            
            return scenes
        
        # Use Claude API
        try:
            client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
            
            user_prompt = f"""Break down this script into structured scenes:

{script_content}

Target total duration: {target_duration} seconds
Style: {style}

Distribute the duration across scenes logically based on their importance.
Ensure the total duration matches the target."""

            message = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                system=SCENE_BREAKDOWN_SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )
            
            response_text = message.content[0].text.strip()
            
            # Extract JSON from response (handle code blocks)
            if response_text.startswith("```"):
                # Remove code block markers
                response_text = re.sub(r'```json\n?', '', response_text)
                response_text = re.sub(r'```\n?', '', response_text)
            
            scenes = json.loads(response_text)
            token_count = message.usage.input_tokens + message.usage.output_tokens
            
            # Log interaction
            await ClaudeService._log_interaction(
                project_id=project_id,
                phase="scene_breakdown",
                user_message=user_prompt,
                claude_response=json.dumps(scenes, indent=2),
                token_count=token_count,
                model="claude-3-5-sonnet-20241022"
            )
            
            return scenes
            
        except Exception as e:
            # Fall back to mock on error
            print(f"Claude API error: {e}, falling back to mock")
            return ClaudeService.generate_mock_scenes(script_content, target_duration, style)
    
    @staticmethod
    async def refine_prompt(
        project_id: str,
        original_prompt: str,
        feedback: str,
        context: Optional[str] = None
    ) -> str:
        """Refine a prompt based on user feedback."""
        # Check if API key is available
        if not ANTHROPIC_API_KEY or not ANTHROPIC_AVAILABLE:
            # Simple mock refinement
            refined = f"{original_prompt} ({feedback})"
            return refined
        
        # Use Claude API
        try:
            client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
            
            user_prompt = f"""Original prompt:
{original_prompt}

User feedback:
{feedback}

{f'Additional context: {context}' if context else ''}

Create an improved version of the prompt that incorporates the feedback."""

            message = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=512,
                system=PROMPT_REFINEMENT_SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )
            
            refined_prompt = message.content[0].text.strip()
            token_count = message.usage.input_tokens + message.usage.output_tokens
            
            # Log interaction
            await ClaudeService._log_interaction(
                project_id=project_id,
                phase="prompt_refinement",
                user_message=user_prompt,
                claude_response=refined_prompt,
                token_count=token_count,
                model="claude-3-5-sonnet-20241022"
            )
            
            return refined_prompt
            
        except Exception as e:
            print(f"Claude API error: {e}, using simple refinement")
            return f"{original_prompt} ({feedback})"
    
    @staticmethod
    async def ensure_consistency(
        project_id: str,
        scenes: List[Dict[str, Any]],
        style: str
    ) -> List[Dict[str, Any]]:
        """Ensure character and style consistency across scenes."""
        # In mock mode or if API unavailable, return as-is
        if not ANTHROPIC_API_KEY or not ANTHROPIC_AVAILABLE:
            return scenes
        
        # Use Claude API for consistency checking
        try:
            client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
            
            user_prompt = f"""Review these scenes for consistency:

{json.dumps(scenes, indent=2)}

Style: {style}

Ensure:
1. Character descriptions match across scenes (if characters appear)
2. Lighting and mood are consistent
3. Visual style is maintained
4. Setting details align

Return the adjusted scenes as a JSON array."""

            message = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                system=CONSISTENCY_CHECK_SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )
            
            response_text = message.content[0].text.strip()
            
            # Extract JSON from response
            if response_text.startswith("```"):
                response_text = re.sub(r'```json\n?', '', response_text)
                response_text = re.sub(r'```\n?', '', response_text)
            
            consistent_scenes = json.loads(response_text)
            token_count = message.usage.input_tokens + message.usage.output_tokens
            
            # Log interaction
            await ClaudeService._log_interaction(
                project_id=project_id,
                phase="consistency_check",
                user_message="Consistency check request",
                claude_response=json.dumps(consistent_scenes, indent=2),
                token_count=token_count,
                model="claude-3-5-sonnet-20241022"
            )
            
            return consistent_scenes
            
        except Exception as e:
            print(f"Claude API error: {e}, returning original scenes")
            return scenes
    
    @staticmethod
    async def _log_interaction(
        project_id: str,
        phase: str,
        user_message: str,
        claude_response: str,
        token_count: int,
        model: str = "claude-3-5-sonnet-20241022"
    ) -> None:
        """Log Claude interaction to database."""
        try:
            async with aiosqlite.connect(DATABASE_PATH) as db:
                await db.execute(
                    """INSERT INTO claude_interactions 
                       (project_id, phase, user_message, claude_response, token_count, model)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (project_id, phase, user_message, claude_response, token_count, model)
                )
                await db.commit()
        except Exception as e:
            print(f"Failed to log Claude interaction: {e}")
