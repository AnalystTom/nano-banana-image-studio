# Plan: Phase 4 - Frame Generation Workflow

## Task Description
Implement the frame generation workflow for the video production CLI, enabling batch image generation with Nano Banana/Gemini API, approval/review loops, and regeneration capabilities. This phase bridges the gap between scene planning (Phase 3) and video generation (Phase 5).

## Objective
Enable users to generate, review, approve, and regenerate key frame images for all scenes in their video project through a streamlined CLI workflow with batch processing, progress tracking, and beautiful Rich terminal UI.

## Problem Statement
After approving scenes, users need a way to:
1. Generate images for all key frames (opening/closing frames per scene) in batch
2. Review generated frames with visual feedback
3. Approve individual frames or provide feedback for regeneration
4. Track progress during long-running batch operations
5. Handle API failures gracefully with automatic retries
6. Store generated images organized by project

The current system creates frame records with status 'pending' but has no mechanism to actually generate, display, or manage these images.

## Solution Approach
Build a comprehensive frame generation system using:
1. **Frame Service** - Database CRUD operations for frame management
2. **Batch Service** - Queue-based processing for concurrent frame generation
3. **Frame Commands** - CLI commands for the complete frame workflow
4. **Integration** - Connect with existing gemini.py for image generation and storage.py for file management
5. **Progress Tracking** - Real-time progress bars using Rich library
6. **Approval Workflow** - Interactive review and regeneration loops

## Relevant Files

### Existing Files to Modify/Use
- **backend/src/services/gemini.py** - Use `generate_image()` for frame generation (already has mock mode)
- **backend/src/services/storage.py** - Use `save_image()` and `generate_filename()` for storing frames
- **backend/src/services/workflow_service.py** - Advance workflow phase after frame approval
- **backend/src/cli/ui/display.py** - Add frame display functions (grid view, detail view)
- **backend/src/cli/ui/prompts.py** - May need additional prompt functions
- **backend/src/cli/main.py** - Register new frame commands
- **backend/src/database.py** - Database schema (frames table already exists)

### New Files to Create
- **backend/src/services/frame_service.py** - Frame database operations (CRUD, status updates, batch queries)
- **backend/src/services/batch_service.py** - Batch job management and processing queue
- **backend/src/cli/commands/frames.py** - Frame CLI commands (generate, show, approve, regenerate)

## Implementation Phases

### Phase 1: Foundation
Build core services for frame and batch management:
- Create `frame_service.py` with database operations
- Create `batch_service.py` with queue processing logic
- Add frame display functions to `display.py`

### Phase 2: Core Implementation
Implement frame generation and approval workflow:
- Create `frames.py` commands module
- Implement batch generation with progress tracking
- Add frame approval and regeneration workflows
- Integrate with gemini.py and storage.py

### Phase 3: Integration & Polish
Wire everything together and test:
- Register commands in `main.py`
- Test end-to-end workflow
- Add error handling and retry logic
- Verify workflow phase advancement

## Step by Step Tasks

### 1. Create Frame Service
- Create `backend/src/services/frame_service.py`
- Implement `get_frame(frame_id)` to retrieve single frame
- Implement `get_frames_for_project(project_id, status_filter)` to list frames
- Implement `get_frames_for_scene(scene_id)` to get scene-specific frames
- Implement `update_frame_status(frame_id, status, image_id)` to track generation progress
- Implement `approve_frame(frame_id)` to mark frame as approved
- Implement `reject_frame(frame_id, feedback)` to request regeneration
- Implement `get_pending_frames(project_id)` to find frames needing generation
- Implement `get_approval_stats(project_id)` to track approval progress
- Follow async patterns from existing services (workflow_service.py, scene_service.py)

### 2. Create Batch Service
- Create `backend/src/services/batch_service.py`
- Implement `create_batch_job(project_id, job_type, total_items)` to initialize jobs
- Implement `update_batch_progress(job_id, completed, failed)` to track progress
- Implement `mark_job_complete(job_id)` to finalize jobs
- Implement `get_batch_status(job_id)` to query job state
- Implement `process_frame_batch(project_id, frames)` for concurrent generation
- Use `asyncio.gather()` for parallel processing (limit concurrency to 5)
- Add retry logic with exponential backoff for failed generations
- Log errors to batch_jobs.error_log field

### 3. Extend Display Functions
- Add to `backend/src/cli/ui/display.py`:
- Implement `display_frames_grid(frames)` to show frames in table format with status
- Implement `display_frame_detail(frame, scene)` to show single frame info
- Implement `display_generation_progress(current, total, status)` for progress tracking
- Add status colors: pending=yellow, generating=blue, completed=green, approved=bright_green, failed=red, rejected=orange
- Use Rich Table for grid view with columns: ID, Scene, Type, Status, Created
- Use Rich Panel for detail view showing full prompt and image path

### 4. Create Frame Commands Module
- Create `backend/src/cli/commands/frames.py`
- Implement `generate_frames(project_id)` command:
  - Get all pending frames for project
  - Create batch job in database
  - Show progress bar with Rich Progress
  - Generate frames concurrently (max 5 at a time)
  - For each frame: call gemini.generate_image(), save with storage.save_image(), update frame record
  - Handle failures with retry (3 attempts)
  - Update batch job progress in real-time
  - Display summary of successful/failed generations
- Implement `show_frames(project_id, scene_filter)` command:
  - Retrieve frames (optionally filtered by scene)
  - Display in grid format with display_frames_grid()
  - Show approval statistics
  - Suggest next commands based on state
- Implement `show_frame(project_id, frame_id)` command:
  - Retrieve frame and associated scene
  - Display detailed view with display_frame_detail()
  - Show generated image path if available
  - Provide action options (approve, reject, regenerate)
- Implement `approve_frame(project_id, frame_id)` command:
  - Update frame status to 'approved'
  - Show confirmation message
  - Check if all frames approved → suggest next step
- Implement `approve_all_frames(project_id)` command:
  - Approve all completed frames in batch
  - Show count of approved frames
  - Advance workflow if all frames approved
- Implement `regenerate_frame(project_id, frame_id, feedback)` command:
  - Mark frame as 'rejected' with feedback
  - Use claude_service.refine_prompt() if feedback provided
  - Regenerate image with new/refined prompt
  - Update frame record with new image
  - Show before/after prompts

### 5. Integrate Image Generation
- In `generate_frames()`:
  - Get project config for aspect_ratio from database
  - Use aspect_ratio from project config (default 16:9)
  - Set resolution to '2K' for quality frames
  - Call `await gemini.generate_image(prompt, aspect_ratio, resolution)`
  - Handle both real API and mock mode gracefully
  - Save image_data using `storage.save_image(image_data, filename)`
  - Create images table entry (reuse existing web API pattern if needed)
  - Link frame to image via image_id foreign key
  - Update frame status to 'completed' or 'failed'

### 6. Implement Progress Tracking
- Use Rich Progress with multiple columns:
  - Spinner for active generation
  - Description with current frame being processed
  - Progress bar showing completion percentage
  - ETA based on average generation time
- Update progress after each frame completes
- Show live status: "Generating frame 3/10 (Scene 2, opening)..."
- Display final summary with success/failure counts

### 7. Add Error Handling and Retry Logic
- Implement retry decorator for API calls (3 attempts, exponential backoff)
- Log failures to batch_jobs.error_log with timestamp and error message
- Continue processing remaining frames if some fail
- Provide clear error messages with suggested actions
- Allow manual retry of failed frames via regenerate command

### 8. Register Commands in Main CLI
- Edit `backend/src/cli/main.py`:
- Import frames module: `from .commands import project, script, scenes, frames`
- Add command: `generate-frames <project_id>`
- Add command: `show-frames <project_id> [--scene N]`
- Add command: `show-frame <project_id> <frame_id>`
- Add command: `approve-frame <project_id> <frame_id>`
- Add command: `approve-all-frames <project_id>`
- Add command: `regenerate-frame <project_id> <frame_id> [--feedback "..."]`
- Follow existing async command pattern with `asyncio.run()`

### 9. Update Workflow Phase Advancement
- In `approve_all_frames()`:
  - Check if ALL frames for project are approved
  - If yes, call `workflow_service.advance_phase(project_id, 'videos')`
  - Update project status to 'videos'
  - Display next steps: "Ready for video generation: nb-studio generate-videos <project_id>"

### 10. Test End-to-End Workflow
- Test with existing Discord Scout project
- Run `nb-studio approve-scenes proj_689daffa9ca5` (if not done)
- Run `nb-studio generate-frames proj_689daffa9ca5`
- Verify progress bar displays correctly
- Verify frames are generated (mock mode OK)
- Run `nb-studio show-frames proj_689daffa9ca5`
- Verify grid display shows all frames
- Run `nb-studio show-frame proj_689daffa9ca5 <frame_id>`
- Verify detail view shows frame info
- Run `nb-studio approve-all-frames proj_689daffa9ca5`
- Verify workflow advances to 'videos' phase
- Check database for correct image_id links and status updates

## Testing Strategy

### Unit Tests
- `test_frame_service.py`:
  - Test frame status updates
  - Test approval/rejection workflows
  - Test frame retrieval with filters
  - Test approval statistics calculation
- `test_batch_service.py`:
  - Test batch job creation and updates
  - Test concurrent frame processing
  - Test retry logic for failures
  - Test progress tracking accuracy

### Integration Tests
- `test_frame_generation_workflow.py`:
  - Test complete generate → approve → advance workflow
  - Test regeneration with feedback
  - Test batch processing with mixed success/failure
  - Test workflow phase advancement triggers

### CLI Tests
- Test all commands with valid/invalid inputs
- Test progress bar rendering (may need to mock)
- Test error messages for missing projects/frames
- Test resume capability after interruption

## Acceptance Criteria
- [ ] Users can generate all pending frames for a project in one command
- [ ] Progress bar shows real-time generation progress with ETA
- [ ] Generated frames are stored in project workspace with proper organization
- [ ] Users can view frames in grid format with status indicators
- [ ] Users can view individual frame details including prompts and image paths
- [ ] Users can approve individual frames or all frames at once
- [ ] Users can regenerate frames with optional feedback for prompt refinement
- [ ] Failed frame generations are automatically retried up to 3 times
- [ ] Batch job progress is tracked in database for resume capability
- [ ] Workflow automatically advances to 'videos' phase when all frames approved
- [ ] All commands display beautiful Rich-formatted output
- [ ] Error messages are clear and actionable
- [ ] Mock mode works without API keys for development

## Validation Commands
Execute these commands to validate the implementation:

### Import and Syntax Checks
```bash
uv run python -c "from src.services.frame_service import FrameService; print('✓ FrameService import successful')"
uv run python -c "from src.services.batch_service import BatchService; print('✓ BatchService import successful')"
uv run python -c "from src.cli.commands.frames import generate_frames; print('✓ Frame commands import successful')"
```

### CLI Command Registration
```bash
uv run nb-studio --help | grep -E "(generate-frames|show-frames|approve-frame)"
```

### End-to-End Workflow Test
```bash
# Create test project
uv run nb-studio create-video --name "E2E Frame Test" << EOF
Test narrative for frame generation
EOF

# Save project ID, then test workflow
PROJECT_ID="<from output>"
uv run nb-studio generate-script $PROJECT_ID
uv run nb-studio approve-script $PROJECT_ID << EOF
y
EOF
uv run nb-studio approve-scenes $PROJECT_ID << EOF
y
EOF
uv run nb-studio generate-frames $PROJECT_ID
uv run nb-studio show-frames $PROJECT_ID
uv run nb-studio approve-all-frames $PROJECT_ID
uv run nb-studio resume $PROJECT_ID  # Should suggest video generation
```

### Database Verification
```bash
uv run python << 'EOFPY'
import asyncio
import aiosqlite

async def check():
    async with aiosqlite.connect('database.db') as db:
        db.row_factory = aiosqlite.Row
        
        # Check frames with images
        cursor = await db.execute("""
            SELECT f.id, f.status, f.image_id, i.filename
            FROM frames f
            LEFT JOIN images i ON f.image_id = i.id
            WHERE f.project_id = '<project_id>'
        """)
        frames = await cursor.fetchall()
        
        print(f"Total frames: {len(frames)}")
        for frame in frames:
            print(f"  Frame {frame['id']}: {frame['status']} - Image: {frame['filename'] or 'None'}")

asyncio.run(check())
EOFPY
```

## Notes

### Dependencies
No new dependencies required. All necessary libraries are already installed:
- `aiosqlite` - Database operations
- `rich` - Terminal UI (Progress, Table, Panel)
- `pillow` - Image handling (via gemini.py)
- `asyncio` - Concurrent processing

### Performance Considerations
- Limit concurrent frame generation to 5 at a time to avoid overwhelming the API
- Use `asyncio.gather()` with semaphore for controlled concurrency
- Mock mode generates frames instantly for testing workflow without API calls
- Consider adding `--dry-run` flag to preview what will be generated without actually generating

### Storage Organization
Frames should be stored in:
```
projects/<project_id>/frames/
  scene_1_opening_<timestamp>.png
  scene_1_closing_<timestamp>.png
  scene_2_opening_<timestamp>.png
  ...
```

Consider updating `storage.py` to support project-specific paths.

### Future Enhancements (Not in Scope)
- Image preview in terminal using ASCII art or external viewer
- Frame comparison tool (compare regenerated vs original)
- Bulk operations on frames (approve by scene, regenerate all rejected)
- Frame versioning (keep history of regenerations)
- Custom aspect ratios per frame (currently uses project default)

### Integration Points
- **From Phase 3**: Receives frame records created by `approve-scenes` command
- **To Phase 5**: Approved frames become reference images for video generation
- **Workflow**: Phase advancement triggers after all frames approved

### Mock Mode Behavior
When `GEMINI_API_KEY` is not set:
- Generates gradient PNG images (like current implementation)
- Completes instantly for fast testing
- Still creates proper database records and file structure
- Displays warning: "⚠ Using mock mode (GEMINI_API_KEY not set)"
