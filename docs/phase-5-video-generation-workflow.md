# Plan: Phase 5 - Video Generation Workflow

## Task Description

Implement scene-level video generation using Google's Veo 3 API (or Veo 2) through the Nano Banana platform. Each scene will generate a short video clip from the approved opening and closing frames, creating smooth transitions and motion.

## Objective

Build a complete video generation system that:
- Generates videos for each scene using approved frames
- Integrates with Google Veo API via Nano Banana
- Manages video rendering queue and progress
- Provides approval workflow for generated videos
- Handles concurrent video generation efficiently
- Stores and organizes video files by project

## Problem Statement

Currently, we have:
- ✅ 5 scenes with descriptions and timing
- ✅ 10 approved frames (2 per scene: opening/closing)
- ✅ Script and narrative structure
- ❌ No video generation capability
- ❌ No video storage/management system
- ❌ No video approval workflow

We need to convert static frames into dynamic video clips that bring the Discord Scout story to life.

## Solution Approach

Use Google's **Veo 3 API** (or Veo 2 if Veo 3 unavailable) to generate videos:
- **Image-to-Video**: Use opening frame as starting point
- **Motion Prompts**: Guide video motion based on scene descriptions
- **Duration Control**: Match scene duration (5-10 seconds)
- **Aspect Ratio**: Maintain 16:9 for consistent output
- **Quality**: 2K or 4K resolution options

## Relevant Files

### Services to Create/Modify
- `backend/src/services/video_service.py` - NEW: Video database operations
- `backend/src/services/video_generation_service.py` - NEW: Veo API integration
- `backend/src/services/gemini.py` - UPDATE: Add Veo video generation

### Commands to Create
- `backend/src/cli/commands/videos.py` - NEW: Video CLI commands

### UI Updates
- `backend/src/cli/ui/display.py` - UPDATE: Add video display functions

### Database Updates
- Existing `scene_videos` table ready to use
- No schema changes needed

## Implementation Phases

### Phase 5A: Veo API Integration
1. Update `gemini.py` with Veo 3 API calls
2. Implement image-to-video generation
3. Add motion prompt engineering
4. Handle video format conversion

### Phase 5B: Video Service Layer
1. Create `video_service.py` for database operations
2. Create `video_generation_service.py` for batch processing
3. Implement video storage management
4. Add video approval tracking

### Phase 5C: CLI Commands
1. Create `videos.py` command module
2. Implement 6 core commands
3. Add Rich progress tracking
4. Integrate with workflow service

### Phase 5D: Testing & Integration
1. Test video generation end-to-end
2. Verify video quality and motion
3. Test approval workflow
4. Validate workflow advancement

## Step by Step Tasks

### Step 1: Update Gemini Service with Veo API

**File:** `backend/src/services/gemini.py`

Add Veo video generation function:

```python
async def generate_video_from_image(
    image_path: str,
    prompt: str,
    duration: str = '5s',
    model: str = 'veo-3.0-generate',
    aspect_ratio: str = '16:9'
) -> dict:
    """
    Generate video using Veo API from a starting image.

    Uses Nano Banana (Google Veo API) with image-to-video.
    """
    if GEMINI_CLIENT:
        try:
            # Load image file
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # Generate video using Veo
            response = GEMINI_CLIENT.models.generate_video(
                model=model,
                prompt=prompt,
                config={
                    'duration': duration,
                    'aspect_ratio': aspect_ratio,
                    'starting_image': image_data,
                }
            )

            if response.generated_videos:
                video = response.generated_videos[0]
                return {
                    'video_data': video.video.data,
                    'duration': duration,
                    'is_mock': False
                }
        except Exception as e:
            print(f"Veo API error: {e}")

    # Fallback to mock
    return generate_mock_video(prompt, aspect_ratio, duration)
```

### Step 2: Create Video Service

**File:** `backend/src/services/video_service.py` (NEW - ~250 lines)

```python
class VideoService:
    """Service for managing scene video database operations."""

    @staticmethod
    async def create_scene_video(
        project_id: str,
        scene_id: int,
        video_filename: str,
        video_path: str,
        prompt: str,
        duration: float,
        status: str = 'completed'
    ) -> int:
        """Create a scene video record."""
        # Insert into scene_videos table
        # Return video_id

    @staticmethod
    async def get_videos_for_project(project_id: str) -> List[Dict]:
        """Get all scene videos for a project."""
        # Query scene_videos with scene info
        # Return list of video records

    @staticmethod
    async def get_video(video_id: int) -> Optional[Dict]:
        """Get single video by ID."""

    @staticmethod
    async def approve_video(video_id: int) -> bool:
        """Mark video as approved."""

    @staticmethod
    async def get_approval_stats(project_id: str) -> Dict[str, int]:
        """Get video approval statistics."""
        # Return counts: total, pending, approved, rejected
```

### Step 3: Create Video Generation Service

**File:** `backend/src/services/video_generation_service.py` (NEW - ~300 lines)

```python
class VideoGenerationService:
    """Service for batch video generation."""

    @staticmethod
    async def generate_scene_video(
        project_id: str,
        scene: Dict[str, Any],
        frames: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a video for a single scene.

        Uses opening frame as starting image and scene description
        as motion prompt for Veo API.
        """
        # Get opening frame image path
        # Create motion prompt from scene description
        # Call Veo API with image-to-video
        # Save video file
        # Create database record
        # Return result

    @staticmethod
    async def process_video_batch(
        project_id: str,
        scenes: List[Dict[str, Any]],
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Generate videos for all scenes in a project.

        Processes sequentially to avoid resource issues.
        """
        # For each scene:
        #   Get frames
        #   Generate video
        #   Update progress
        # Return batch results
```

### Step 4: Update Display Functions

**File:** `backend/src/cli/ui/display.py`

Add video display functions:

```python
def display_videos_grid(videos: List[Dict[str, Any]], stats: Optional[Dict] = None):
    """Display videos in table format."""
    # Rich table with: Scene, Duration, Status, Filename
    # Include statistics panel

def display_video_detail(video: Dict[str, Any], scene: Optional[Dict] = None):
    """Display detailed video information."""
    # Video info panel
    # Motion prompt panel
    # Scene context panel
```

### Step 5: Create Video Commands

**File:** `backend/src/cli/commands/videos.py` (NEW - ~400 lines)

Implement 6 commands:

1. **`generate-videos`** - Generate all scene videos
   ```python
   async def generate_videos(project_id: str):
       # Get all scenes with approved frames
       # Check for pending videos
       # Confirm with user
       # Generate videos with progress bar
       # Display results
   ```

2. **`show-videos`** - Display all videos
   ```python
   async def show_videos(project_id: str, scene: Optional[int] = None):
       # Get videos for project/scene
       # Display grid with stats
       # Show next actions
   ```

3. **`show-video`** - Display single video details
   ```python
   async def show_video(project_id: str, video_id: int):
       # Get video record
       # Get scene context
       # Display detailed view
   ```

4. **`approve-video`** - Approve single video
   ```python
   async def approve_video(project_id: str, video_id: int):
       # Approve video
       # Check if all approved
       # Advance workflow if complete
   ```

5. **`approve-all-videos`** - Batch approve
   ```python
   async def approve_all_videos(project_id: str):
       # Get all completed videos
       # Confirm with user
       # Approve all
       # Advance to assembly phase
   ```

6. **`regenerate-video`** - Regenerate with new prompt
   ```python
   async def regenerate_video(
       project_id: str,
       video_id: int,
       motion_prompt: Optional[str] = None
   ):
       # Get current video
       # Refine motion prompt if provided
       # Regenerate video
       # Update database
   ```

### Step 6: Register Video Commands

**File:** `backend/src/cli/main.py`

Add command registrations:

```python
from .commands import project, script, scenes, frames, videos

@app.command("generate-videos")
def generate_videos_command(project_id: str = typer.Argument(...)):
    """Generate scene videos for the project."""
    asyncio.run(videos.generate_videos(project_id=project_id))

@app.command("show-videos")
def show_videos_command(
    project_id: str = typer.Argument(...),
    scene: Optional[int] = typer.Option(None, "--scene", "-s")
):
    """Show all scene videos."""
    asyncio.run(videos.show_videos(project_id=project_id, scene=scene))

# ... 4 more command registrations
```

### Step 7: Update Workflow Advancement

Ensure `approve-all-videos` advances workflow from `videos` → `assembly`:

```python
# In approve_all_videos after all approved
await WorkflowService.advance_phase(project_id, 'assembly')
print_success("✓ Workflow advanced to 'assembly' phase")
```

### Step 8: Test Video Generation

Test with Discord Scout project:

```bash
# Ensure frames are approved
nb-studio approve-all-frames proj_689daffa9ca5

# Generate videos
nb-studio generate-videos proj_689daffa9ca5

# Review results
nb-studio show-videos proj_689daffa9ca5

# Approve all
nb-studio approve-all-videos proj_689daffa9ca5
```

### Step 9: Create Video Storage Organization

Structure videos by project:

```
backend/static/videos/
├── scene_1_20260104_143022_abc123.mp4
├── scene_2_20260104_143045_def456.mp4
├── scene_3_20260104_143108_ghi789.mp4
├── scene_4_20260104_143131_jkl012.mp4
└── scene_5_20260104_143154_mno345.mp4
```

### Step 10: Add Mock Video Generation

For development without Veo API access:

```python
def generate_mock_video(
    prompt: str,
    aspect_ratio: str = '16:9',
    duration: str = '5s'
) -> tuple:
    """Generate mock video (animated gradient GIF)."""
    # Create frames with animated gradients
    # Save as GIF or MP4
    # Return video_data, metadata
```

## Testing Strategy

### Unit Tests
- Test video database operations
- Test Veo API integration (mocked)
- Test video storage functions
- Test approval workflows

### Integration Tests
- Test video generation service with mock API
- Test CLI commands
- Test workflow advancement
- Test error handling

### End-to-End Test
1. Start with approved frames
2. Generate all scene videos
3. Review video grid
4. Approve videos
5. Verify workflow advancement
6. Check video file storage

## Acceptance Criteria

- [ ] Veo API integration working or graceful mock fallback
- [ ] Video generation for all 5 scenes
- [ ] Video files stored with proper naming
- [ ] Database records created for all videos
- [ ] CLI commands functional (6 commands)
- [ ] Progress tracking with Rich progress bars
- [ ] Approval workflow complete
- [ ] Workflow advances to assembly phase
- [ ] Error handling and retry logic
- [ ] Mock mode for development
- [ ] Video quality acceptable (2K minimum)
- [ ] Duration matches scene timing
- [ ] Aspect ratio correct (16:9)

## Validation Commands

```bash
# Check project status
nb-studio show-project proj_689daffa9ca5

# Generate videos
nb-studio generate-videos proj_689daffa9ca5

# View all videos
nb-studio show-videos proj_689daffa9ca5

# View single video
nb-studio show-video proj_689daffa9ca5 <video_id>

# Approve video
nb-studio approve-video proj_689daffa9ca5 <video_id>

# Approve all videos
nb-studio approve-all-videos proj_689daffa9ca5

# Regenerate with custom prompt
nb-studio regenerate-video proj_689daffa9ca5 <video_id> --motion-prompt "..."

# Check final status
nb-studio show-project proj_689daffa9ca5
# Should show: Status: assembly
```

## Notes

### Veo API Considerations
- **Veo 3** preferred for best quality
- **Veo 2** fallback if Veo 3 unavailable
- Image-to-video requires starting image
- Motion prompts guide video generation
- Duration: 5-10 seconds typical
- Resolution: 2K or 4K options

### Performance
- Video generation is slower than image generation (~30-60s per video)
- Sequential processing recommended (concurrency=1)
- Total time for 5 videos: ~3-5 minutes

### Storage
- Videos are larger than images (5-50 MB per video)
- Use MP4 format for compatibility
- GIF for mock mode (smaller size)

### Cost Management
- Veo API can be expensive
- Mock mode for development
- Batch generation to minimize API calls
- Cache generated videos

### Email Configuration
User email for API access: `tradingtoptom999@gmail.com`
- May be needed for Veo API authentication
- Could be used for quota management
- Check if API key is tied to this email

## Integration Points

### Existing Services
- `gemini.py` - Add Veo video generation
- `workflow_service.py` - Advance to assembly phase
- `storage.py` - Video file management

### New Services
- `video_service.py` - Database operations
- `video_generation_service.py` - Batch processing

### Database Schema
- `scene_videos` table already exists
- No migrations needed

### CLI Structure
```
nb-studio
├── generate-videos      (NEW)
├── show-videos          (NEW)
├── show-video           (NEW)
├── approve-video        (NEW)
├── approve-all-videos   (NEW)
└── regenerate-video     (NEW)
```

## Success Metrics
- 5/5 scene videos generated
- 100% approval rate
- Workflow advanced to assembly
- All videos stored correctly
- 0 errors during generation
- Processing time < 10 minutes total

---

**Status:** Ready for implementation
**Estimated Time:** 4-6 hours
**Prerequisites:** Phase 4 complete (frames approved)
**Next Phase:** Phase 6 - Final Video Assembly
