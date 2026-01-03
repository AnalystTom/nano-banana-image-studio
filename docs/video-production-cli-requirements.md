# Video Production CLI - Requirements & Planning Document

**Project**: Nano Banana Image Studio - Video Production CLI
**Version**: 1.0
**Date**: 2026-01-03
**Status**: Planning Phase

---

## 1. USER JOURNEY

### 1.1 High-Level User Story

**As a** content creator
**I want to** generate professional short-form videos through an AI-assisted workflow
**So that** I can create polished video content from a simple narrative description without manual editing tools

### 1.2 End-to-End User Journey Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                    VIDEO PRODUCTION WORKFLOW                         │
└─────────────────────────────────────────────────────────────────────┘

Phase 1: PROJECT INITIALIZATION
├─ User runs: `nb-studio create-video "My Video Concept"`
├─ CLI prompts for project details:
│  ├─ Project name
│  ├─ Main narrative/story
│  ├─ Target duration (15s, 30s, 60s)
│  ├─ Style themes (cinematic, minimal, vibrant, etc.)
│  └─ Aspect ratio (16:9, 9:16, 1:1)
└─ System creates new project workspace
   └─ Output: "Project 'my-video' created (ID: proj_abc123)"

Phase 2: SCRIPT GENERATION & REVIEW
├─ Claude generates detailed script with scene breakdown
├─ User reviews script in interactive mode:
│  ├─ View full script
│  ├─ See scene-by-scene breakdown
│  └─ Provide feedback: "Make scene 3 more dramatic"
├─ Claude refines script based on feedback
└─ User approves: `approve-script`
   └─ Output: "Script locked. 5 scenes identified."

Phase 3: SCENE PLANNING
├─ For each scene, Claude generates:
│  ├─ Opening frame description
│  ├─ Closing frame description
│  ├─ Camera movement/angle
│  ├─ Duration
│  └─ Character/object consistency notes
├─ User reviews scene plan:
│  └─ `show-scenes` displays table of all scenes
└─ User approves: `approve-scenes`
   └─ Output: "10 key frames identified for generation"

Phase 4: IMAGE GENERATION (KEY FRAMES)
├─ System generates opening/closing images for each scene
├─ Progress: "Generating frame 1/10..."
├─ User reviews generated images:
│  ├─ `show-frames` displays grid of all frames
│  ├─ `review-frame 3` shows detailed view
│  └─ User feedback options:
│     ├─ Approve: `approve-frame 3`
│     ├─ Regenerate: `regenerate-frame 3 "make darker"`
│     └─ Regenerate all: `regenerate-all-frames`
├─ Iterative refinement loop per frame
└─ User approves all: `approve-all-frames`
   └─ Output: "All frames approved. Ready for video generation."

Phase 5: VIDEO GENERATION
├─ System generates video for each scene using key frames
├─ Progress: "Generating scene 1/5 video..."
├─ User reviews generated videos:
│  ├─ `show-videos` displays list with thumbnails
│  ├─ `play-video scene-2` opens video preview
│  └─ User feedback options:
│     ├─ Approve: `approve-video scene-2`
│     ├─ Regenerate: `regenerate-video scene-2 --prompt "slower pan"`
│     └─ Trim: `trim-video scene-2 --start 0.5 --end 4.5`
└─ User approves all: `approve-all-videos`
   └─ Output: "All scene videos approved."

Phase 6: VIDEO ASSEMBLY & FINALIZATION
├─ User reviews scene order: `show-timeline`
├─ Optional editing:
│  ├─ Reorder: `move-scene 3 to 2`
│  ├─ Remove: `remove-scene 4`
│  └─ Add transition: `add-transition scene-1 scene-2 --type fade`
├─ System compiles final video
└─ User exports: `export-video --format mp4 --quality high`
   └─ Output: "Video exported: outputs/my-video-final.mp4"

Phase 7: ITERATION (Optional)
├─ User can revisit any phase:
│  ├─ `edit-script` - Back to Phase 2
│  ├─ `regenerate-frame 2` - Back to Phase 4 for specific frame
│  └─ `regenerate-scene 3` - Back to Phase 5 for specific scene
└─ System maintains version history
```

### 1.3 User Personas

**Persona 1: Solo Content Creator**
- Creates social media content (TikTok, Instagram Reels, YouTube Shorts)
- Limited video editing experience
- Needs fast turnaround (30-60 min per video)
- Values consistency in style and characters

**Persona 2: Marketing Professional**
- Produces explainer videos for products
- Needs precise control over messaging
- Works with brand guidelines (colors, fonts, style)
- Requires approval workflow for stakeholders

**Persona 3: Educator/Trainer**
- Creates educational content
- Needs clear visual storytelling
- Values accuracy over artistic flair
- Wants to iterate on specific scenes

### 1.4 Key User Pain Points Addressed

| Pain Point | Solution |
|------------|----------|
| Manual video editing is time-consuming | Automated video generation from text |
| Inconsistent visual style across scenes | Style preservation through project settings |
| Character consistency issues | Character template reuse across scenes |
| Difficult to preview before final render | Frame-by-frame review before video generation |
| No easy way to iterate on specific parts | Granular control: regenerate individual frames/scenes |
| Complex tools with steep learning curve | CLI with guided workflow and clear commands |

---

## 2. DESIGN & STYLE

### 2.1 CLI Design Philosophy

**Principles:**
1. **Progressive Disclosure**: Start simple, reveal complexity as needed
2. **Conversational Flow**: Feel like working with a director, not a command line
3. **Visual Feedback**: Rich terminal output with colors, tables, progress bars
4. **Forgiving**: Easy undo, regenerate, and iterate
5. **Transparent**: Show what AI is doing at each step

### 2.2 CLI Interface Style

**Framework**: Typer (Python) for type-safe, beautiful CLIs
**Visual Components**:
- **Rich** library for:
  - Progress bars with ETA
  - Syntax-highlighted output
  - Formatted tables (scene breakdown, frame status)
  - Panels for section grouping
  - Console markup for colors/emphasis
  - Live displays for real-time updates

**Example Output Styles:**

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🎬 Video Production Workflow - Phase 2/7   ┃
┃  Project: my-awesome-video                  ┃
┃  Status: Script Generation                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

[Claude is writing your script...]

┌─ Generated Script ──────────────────────────┐
│                                             │
│ Scene 1: Opening (0:00-0:05)                │
│ A sunrise over mountains, camera slowly     │
│ panning right. Warm golden tones.           │
│                                             │
│ Scene 2: Introduction (0:05-0:15)           │
│ Close-up of protagonist walking through     │
│ forest. Natural lighting, green palette.    │
│                                             │
│ ... (3 more scenes)                         │
└─────────────────────────────────────────────┘

✓ Script generated (5 scenes, ~30 seconds)

Options:
  [a] Approve and continue
  [f] Provide feedback
  [r] Regenerate completely
  [q] Quit

Your choice:
```

### 2.3 Visual Design Elements

**Color Scheme** (using Rich markup):
- `[green]` - Success messages, approved items
- `[yellow]` - Warnings, pending review
- `[red]` - Errors, rejected items
- `[blue]` - Informational, system messages
- `[magenta]` - AI responses, Claude's voice
- `[cyan]` - User prompts and inputs

**Icons/Emojis** (optional, toggleable):
- 🎬 Video/production
- 📝 Script/text
- 🖼️ Image/frame
- ✅ Approved
- ⏳ In progress
- ❌ Error
- 🔄 Regenerating
- 💡 Tip/suggestion

**Layout Patterns**:
1. **Status Header**: Always show current project, phase, progress
2. **Content Area**: Main output (script, frames, videos)
3. **Action Footer**: Available commands/options
4. **Sidebar** (for wide terminals): Quick stats, recently approved items

### 2.4 Interactive Modes

**Mode 1: Wizard Mode (Default for beginners)**
- Guided step-by-step prompts
- Contextual help at each step
- Limited choices to prevent overwhelm
- Example: `nb-studio create-video --wizard`

**Mode 2: Expert Mode**
- All options available upfront
- Batch operations supported
- Assumes familiarity with workflow
- Example: `nb-studio create-video --script "script.txt" --auto-approve-frames`

**Mode 3: Watch Mode**
- Automatically regenerate on file changes
- Useful for iterative refinement
- Example: `nb-studio watch --project my-video`

### 2.5 Output Formats

**Terminal Output:**
- Human-readable tables and panels
- Color-coded status indicators
- Progress bars for long operations

**File Outputs:**
- `project.json` - Project metadata and settings
- `script.md` - Generated script in markdown
- `scenes.json` - Scene breakdown with frame references
- `timeline.json` - Final video composition data
- `frames/` - Directory of generated images
- `videos/` - Directory of generated scene videos
- `output/` - Final compiled video

**Log Files:**
- `production.log` - Detailed operation log
- `claude-feedback.log` - All AI interactions
- `errors.log` - Error tracking

---

## 3. CORE FUNCTIONALITY

### 3.1 Functional Requirements

#### FR1: Project Management
- **FR1.1**: Create new video production project with unique ID
- **FR1.2**: Store project configuration (name, style, ratio, duration target)
- **FR1.3**: List all projects with status summary
- **FR1.4**: Delete/archive projects
- **FR1.5**: Resume interrupted projects
- **FR1.6**: Export project for backup/sharing

#### FR2: Script Generation
- **FR2.1**: Accept user narrative/concept as input
- **FR2.2**: Generate structured script using Claude
- **FR2.3**: Break script into logical scenes (based on duration target)
- **FR2.4**: Allow iterative refinement via conversational feedback
- **FR2.5**: Lock script to prevent accidental changes
- **FR2.6**: Version control for script iterations

#### FR3: Scene Planning
- **FR3.1**: Parse approved script into scenes
- **FR3.2**: For each scene, generate:
  - Opening frame description (detailed prompt)
  - Closing frame description (detailed prompt)
  - Camera movement/angle specification
  - Scene duration
  - Transition type (cut, fade, dissolve)
- **FR3.3**: Ensure character consistency across scenes
- **FR3.4**: Apply style theme to all scene descriptions
- **FR3.5**: Allow manual editing of individual scene descriptions
- **FR3.6**: Validate scene continuity (lighting, character positions, etc.)

#### FR4: Image Generation (Key Frames)
- **FR4.1**: Generate images using Nano Banana API
- **FR4.2**: Support batch generation with queue management
- **FR4.3**: Retry failed generations automatically (up to 3 attempts)
- **FR4.4**: Display progress with ETA for batch operations
- **FR4.5**: Allow selective regeneration of individual frames
- **FR4.6**: Bulk regeneration with modified prompts
- **FR4.7**: Store frame metadata (prompt, model, settings)
- **FR4.8**: Preview frames in terminal (ASCII art or external viewer)

#### FR5: Frame Review & Approval
- **FR5.1**: Display frames in grid view with status indicators
- **FR5.2**: Zoom into individual frame for detailed review
- **FR5.3**: Approve/reject individual frames
- **FR5.4**: Provide feedback for regeneration
- **FR5.5**: Compare frame versions side-by-side
- **FR5.6**: Bulk approve all frames
- **FR5.7**: Track approval state in database

#### FR6: Video Generation
- **FR6.1**: Generate videos using Veo3 API
- **FR6.2**: Use opening frame as reference for video generation
- **FR6.3**: Support multiple aspect ratios (16:9, 9:16, 1:1)
- **FR6.4**: Support duration options (5s, 8s per scene)
- **FR6.5**: Apply consistent style across all scene videos
- **FR6.6**: Preserve character consistency via reference images
- **FR6.7**: Handle API rate limits and quotas gracefully
- **FR6.8**: Store video metadata (prompt, model, settings, generation time)

#### FR7: Video Review & Editing
- **FR7.1**: Preview generated scene videos in player
- **FR7.2**: Trim individual scene videos (start/end points)
- **FR7.3**: Regenerate specific scenes with modified prompts
- **FR7.4**: Adjust scene order in timeline
- **FR7.5**: Remove scenes from final compilation
- **FR7.6**: Add basic transitions between scenes
- **FR7.7**: Approve/reject individual scene videos

#### FR8: Video Assembly
- **FR8.1**: Compile approved scene videos into single file
- **FR8.2**: Apply transitions between scenes
- **FR8.3**: Validate total duration matches target
- **FR8.4**: Support multiple output formats (MP4, MOV, WebM)
- **FR8.5**: Support quality presets (draft, standard, high)
- **FR8.6**: Generate thumbnail for final video
- **FR8.7**: Export metadata file with production details

#### FR9: Claude Integration
- **FR9.1**: Use Claude for script generation from narrative
- **FR9.2**: Use Claude for scene breakdown and frame descriptions
- **FR9.3**: Use Claude to refine prompts based on user feedback
- **FR9.4**: Use Claude to ensure consistency across scenes
- **FR9.5**: Use Claude to suggest improvements at each phase
- **FR9.6**: Store all Claude interactions for audit trail
- **FR9.7**: Allow user to configure Claude's creativity level

#### FR10: Workflow State Management
- **FR10.1**: Track workflow phase (script → scenes → frames → videos → assembly)
- **FR10.2**: Allow navigation to any phase
- **FR10.3**: Prevent skipping required approval steps
- **FR10.4**: Save state automatically at each step
- **FR10.5**: Resume from last checkpoint on CLI restart
- **FR10.6**: Rollback to previous phase if needed

#### FR11: Configuration & Templates
- **FR11.1**: Define reusable style templates (cinematic, minimal, etc.)
- **FR11.2**: Define character templates for consistency
- **FR11.3**: Save project presets (aspect ratio, duration, model preferences)
- **FR11.4**: Import/export configuration files
- **FR11.5**: Override global settings per project

#### FR12: Error Handling & Recovery
- **FR12.1**: Graceful handling of API failures
- **FR12.2**: Automatic retry with exponential backoff
- **FR12.3**: Queue failed operations for manual retry
- **FR12.4**: Display clear error messages with suggested actions
- **FR12.5**: Log all errors with context for debugging
- **FR12.6**: Validate inputs before API calls

### 3.2 Non-Functional Requirements

#### NFR1: Performance
- **NFR1.1**: CLI startup time < 2 seconds
- **NFR1.2**: Frame generation queue processes 5+ frames concurrently
- **NFR1.3**: Video compilation time < 5 minutes for 30s video
- **NFR1.4**: Database queries < 100ms for typical operations
- **NFR1.5**: Responsive UI even during background operations

#### NFR2: Usability
- **NFR2.1**: First-time users can create video in < 15 minutes
- **NFR2.2**: All commands have `--help` documentation
- **NFR2.3**: Error messages include actionable next steps
- **NFR2.4**: Workflow progress visible at all times
- **NFR2.5**: Keyboard shortcuts for common actions

#### NFR3: Reliability
- **NFR3.1**: Project state persisted after every phase
- **NFR3.2**: Graceful shutdown preserves progress
- **NFR3.3**: Corrupted files don't crash CLI
- **NFR3.4**: 99% success rate for API calls (with retries)

#### NFR4: Maintainability
- **NFR4.1**: Modular service architecture (reuse existing services)
- **NFR4.2**: Comprehensive logging for debugging
- **NFR4.3**: Type hints for all Python code
- **NFR4.4**: Unit tests for critical workflows
- **NFR4.5**: Integration tests for end-to-end flow

#### NFR5: Compatibility
- **NFR5.1**: Support Python 3.11+
- **NFR5.2**: Cross-platform (Linux, macOS, Windows)
- **NFR5.3**: Graceful degradation on terminals without color support
- **NFR5.4**: Compatible with existing backend services

### 3.3 API Integrations Required

#### Claude (Anthropic)
- **Purpose**: Script generation, scene planning, feedback processing
- **Endpoints**: Messages API (claude-3-5-sonnet or claude-opus-4)
- **Data Flow**: User narrative → Claude → Structured script
- **Rate Limits**: Handle token limits for long conversations

#### Nano Banana / Gemini
- **Purpose**: Image generation for key frames
- **Endpoints**:
  - `/api/generate` (existing)
  - Gemini 2.5 Flash Image or Gemini 3 Pro Image
- **Data Flow**: Frame description → Nano Banana → Image file
- **Rate Limits**: Batch queue to respect API quotas

#### Veo3 (Google)
- **Purpose**: Video generation for scenes
- **Endpoints**:
  - `/api/generate-video` (existing skeleton)
  - Veo 3.0 Generate API (needs integration)
- **Data Flow**: Opening frame + prompt → Veo3 → Video file
- **Rate Limits**: Sequential generation with retry logic

#### FFmpeg (Local)
- **Purpose**: Video assembly, trimming, transitions
- **Usage**: Command-line tool via subprocess
- **Operations**:
  - Concatenate scene videos
  - Apply transitions (crossfade, fade in/out)
  - Trim videos to exact durations
  - Convert formats and quality levels

### 3.4 Database Schema Extensions

**New Tables Needed:**

```sql
-- Projects: Top-level container for video productions
CREATE TABLE projects (
    id TEXT PRIMARY KEY,                    -- e.g., proj_abc123
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,                   -- planning, script, frames, videos, assembly, completed
    config JSON NOT NULL,                   -- Project settings (style, ratio, duration, etc.)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Scripts: Generated scripts with versioning
CREATE TABLE scripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    content TEXT NOT NULL,                  -- Full script text
    scene_count INTEGER,
    approved BOOLEAN DEFAULT 0,
    approved_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Scenes: Breakdown of script into scenes
CREATE TABLE scenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    script_id INTEGER NOT NULL,
    scene_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    opening_frame_prompt TEXT NOT NULL,     -- Prompt for opening image
    closing_frame_prompt TEXT,              -- Prompt for closing image (optional)
    camera_direction TEXT,                  -- pan-left, zoom-in, static, etc.
    duration REAL NOT NULL,                 -- Duration in seconds
    transition_type TEXT DEFAULT 'cut',     -- cut, fade, dissolve
    order_index INTEGER NOT NULL,           -- For reordering
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (script_id) REFERENCES scripts(id) ON DELETE CASCADE
);

-- Frames: Generated images (key frames for scenes)
CREATE TABLE frames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    scene_id INTEGER NOT NULL,
    frame_type TEXT NOT NULL,               -- 'opening' or 'closing'
    image_id INTEGER,                       -- FK to existing images table
    prompt TEXT NOT NULL,
    status TEXT NOT NULL,                   -- pending, generating, completed, failed, approved, rejected
    approval_feedback TEXT,                 -- User feedback if rejected
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (scene_id) REFERENCES scenes(id) ON DELETE CASCADE,
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE SET NULL
);

-- Scene Videos: Generated videos for each scene
CREATE TABLE scene_videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    scene_id INTEGER NOT NULL,
    video_id INTEGER,                       -- FK to existing videos table
    reference_frame_id INTEGER,             -- FK to frames table (opening frame)
    prompt TEXT NOT NULL,
    status TEXT NOT NULL,                   -- pending, generating, completed, failed, approved, rejected
    trim_start REAL DEFAULT 0,              -- Trim start time in seconds
    trim_end REAL,                          -- Trim end time in seconds
    approval_feedback TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (scene_id) REFERENCES scenes(id) ON DELETE CASCADE,
    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE SET NULL,
    FOREIGN KEY (reference_frame_id) REFERENCES frames(id) ON DELETE SET NULL
);

-- Workflows: State machine tracking for productions
CREATE TABLE workflows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL UNIQUE,
    current_phase TEXT NOT NULL,            -- script_gen, scene_planning, frame_gen, frame_review, video_gen, video_review, assembly
    phase_data JSON,                        -- Phase-specific state data
    checkpoint TEXT,                        -- Last successful checkpoint
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Claude Interactions: Audit trail of AI conversations
CREATE TABLE claude_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    phase TEXT NOT NULL,
    user_message TEXT,
    claude_response TEXT,
    token_count INTEGER,
    model TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Style Templates: Reusable style presets
CREATE TABLE style_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    style_keywords TEXT NOT NULL,           -- e.g., "cinematic, warm tones, dramatic lighting"
    camera_preferences TEXT,                -- Default camera movements
    color_palette TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Character Templates: Consistent character descriptions
CREATE TABLE character_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT,                        -- NULL for global templates
    name TEXT NOT NULL,
    description TEXT NOT NULL,              -- Detailed character description
    reference_image_id INTEGER,             -- FK to images table
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (reference_image_id) REFERENCES images(id) ON DELETE SET NULL
);

-- Batch Jobs: Queue for async operations
CREATE TABLE batch_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    job_type TEXT NOT NULL,                 -- frame_generation, video_generation
    status TEXT NOT NULL,                   -- queued, running, completed, failed
    total_items INTEGER NOT NULL,
    completed_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0,
    error_log TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

### 3.5 Service Layer Architecture

**New Services to Build:**

```python
# services/claude_service.py
async def generate_script(narrative: str, config: dict) -> str
async def breakdown_into_scenes(script: str, target_duration: int) -> List[Scene]
async def generate_frame_prompts(scene: Scene, style: str, characters: List[Character]) -> FramePrompts
async def refine_based_on_feedback(item: str, feedback: str) -> str
async def ensure_consistency(scenes: List[Scene]) -> List[Scene]

# services/script_service.py
async def create_script(project_id: str, content: str) -> Script
async def get_script_versions(project_id: str) -> List[Script]
async def approve_script(script_id: int) -> Script
async def parse_scenes_from_script(script: Script) -> List[Scene]

# services/scene_service.py
async def create_scenes(project_id: str, script_id: int, scenes: List[SceneData]) -> List[Scene]
async def get_scenes_for_project(project_id: str) -> List[Scene]
async def reorder_scenes(project_id: str, new_order: List[int]) -> None
async def update_scene(scene_id: int, updates: dict) -> Scene

# services/frame_service.py
async def generate_frame(frame_id: int) -> Frame
async def batch_generate_frames(project_id: str) -> BatchJob
async def approve_frame(frame_id: int) -> Frame
async def reject_frame(frame_id: int, feedback: str) -> Frame
async def regenerate_frame(frame_id: int, modified_prompt: str) -> Frame
async def get_frames_for_scene(scene_id: int) -> List[Frame]

# services/video_service.py (extend existing)
async def generate_scene_video(scene_video_id: int, reference_frame: Frame) -> SceneVideo
async def batch_generate_videos(project_id: str) -> BatchJob
async def approve_video(scene_video_id: int) -> SceneVideo
async def trim_video(scene_video_id: int, start: float, end: float) -> SceneVideo
async def regenerate_video(scene_video_id: int, modified_prompt: str) -> SceneVideo

# services/assembly_service.py
async def compile_final_video(project_id: str, output_path: str, quality: str) -> str
async def add_transitions(scenes: List[SceneVideo]) -> None
async def validate_timeline(project_id: str) -> dict

# services/workflow_service.py
async def create_workflow(project_id: str) -> Workflow
async def get_workflow(project_id: str) -> Workflow
async def advance_phase(project_id: str, next_phase: str) -> Workflow
async def checkpoint(project_id: str) -> None
async def rollback_phase(project_id: str, target_phase: str) -> Workflow

# services/batch_service.py
async def create_batch_job(project_id: str, job_type: str, items: List) -> BatchJob
async def process_batch_job(job_id: int) -> None
async def get_batch_status(job_id: int) -> BatchJob
async def retry_failed_items(job_id: int) -> None
```

**Reuse Existing Services:**
- `gemini.py` - For image generation (FR4)
- `storage.py` - For file management
- Database layer - For persistence

---

## 4. USER ACCEPTANCE CRITERIA

### 4.1 Feature-Level Acceptance Criteria

#### AC1: Project Creation
```gherkin
GIVEN I want to create a new video
WHEN I run `nb-studio create-video --name "My Video"`
THEN the system creates a new project
AND assigns a unique project ID
AND initializes the project directory structure
AND displays the project ID and next steps
```

#### AC2: Script Generation
```gherkin
GIVEN I have created a project
WHEN I provide a narrative description
THEN Claude generates a complete script
AND breaks it into logical scenes
AND displays the script for review
AND allows me to provide feedback
AND regenerates based on feedback
AND lets me approve when satisfied
```

#### AC3: Scene Planning
```gherkin
GIVEN I have approved the script
WHEN the system processes the script
THEN it identifies all scenes
AND generates opening frame prompts for each scene
AND generates closing frame prompts where applicable
AND displays a scene breakdown table
AND allows me to edit individual scene descriptions
AND validates character and style consistency
```

#### AC4: Frame Generation
```gherkin
GIVEN I have approved the scene plan
WHEN I trigger frame generation
THEN the system generates images for all key frames
AND displays progress with ETA
AND handles API failures with retries
AND shows me a grid of generated frames
AND allows me to review each frame individually
AND lets me regenerate specific frames with feedback
AND tracks approval status for each frame
```

#### AC5: Video Generation
```gherkin
GIVEN I have approved all frames
WHEN I trigger video generation
THEN the system generates videos for each scene
AND uses opening frames as references
AND applies consistent style across scenes
AND preserves character consistency
AND displays progress with ETA
AND handles API rate limits gracefully
AND shows me preview links for each video
AND allows me to approve or regenerate each video
```

#### AC6: Video Assembly
```gherkin
GIVEN I have approved all scene videos
WHEN I trigger final assembly
THEN the system compiles videos into a single file
AND applies transitions between scenes
AND matches the target duration
AND generates output in requested format/quality
AND provides the final video file path
AND creates a thumbnail for the video
```

#### AC7: Workflow State
```gherkin
GIVEN I am working on a project
WHEN I exit the CLI mid-workflow
THEN the system saves my progress
AND when I restart and resume the project
THEN I continue from the last checkpoint
AND all approvals and generated assets are preserved
```

#### AC8: Error Recovery
```gherkin
GIVEN an API call fails during generation
WHEN the system encounters the error
THEN it automatically retries up to 3 times
AND if still failing, it marks the item as failed
AND displays a clear error message
AND allows me to manually retry later
AND logs the error for debugging
```

#### AC9: Iterative Refinement
```gherkin
GIVEN I have completed video assembly
WHEN I want to improve a specific scene
THEN I can navigate back to that scene
AND regenerate its frames or video
AND the system maintains the rest of the project
AND re-assembles the final video with the update
```

### 4.2 Quality Acceptance Criteria

#### QAC1: Visual Consistency
```
GIVEN a project with 5 scenes
WHEN all videos are generated
THEN character appearance is consistent across scenes (95%+ similarity)
AND style/color palette matches across scenes
AND lighting direction is coherent
```

#### QAC2: Performance Benchmarks
```
GIVEN a 30-second video project (5 scenes, 10 frames)
THEN script generation completes in < 30 seconds
AND frame generation batch completes in < 10 minutes
AND video generation batch completes in < 20 minutes
AND final assembly completes in < 5 minutes
AND total workflow (no iterations) completes in < 40 minutes
```

#### QAC3: Reliability
```
GIVEN 100 API calls across all operations
THEN at least 95 succeed on first attempt
AND 99 succeed after retries
AND all failures are logged with context
```

#### QAC4: Usability
```
GIVEN a new user with no prior CLI experience
WHEN using wizard mode
THEN they can complete their first video in < 1 hour
AND without reading documentation
AND with clear guidance at each step
```

### 4.3 Integration Acceptance Criteria

#### IAC1: Claude Integration
```
GIVEN any script generation request
THEN Claude is called with appropriate system prompt
AND response is parsed into structured scenes
AND character/style consistency is enforced in prompts
AND all interactions are logged
```

#### IAC2: Nano Banana Integration
```
GIVEN a frame generation request
THEN Nano Banana API is called with correct parameters
AND response image is stored in project frames directory
AND metadata is saved to database
AND failed generations are queued for retry
```

#### IAC3: Veo3 Integration
```
GIVEN a video generation request with reference frame
THEN Veo3 API is called with opening frame as image prompt
AND style/camera parameters are included
AND response video is stored in project videos directory
AND metadata is saved to database
```

#### IAC4: FFmpeg Integration
```
GIVEN approved scene videos ready for assembly
THEN FFmpeg is invoked to concatenate videos
AND transitions are applied correctly
AND output quality matches requested preset
AND no artifacts or corruption in final video
```

---

## 5. END-TO-END FLOW & KEY TESTS

### 5.1 Critical User Paths

#### Path 1: Happy Path (No Iterations)
```
1. User creates project
2. Provides narrative
3. Approves generated script on first try
4. Approves scene plan on first try
5. Approves all generated frames on first try
6. Approves all generated videos on first try
7. Exports final video
8. Success ✓

Expected Duration: ~40 minutes for 30s video
Test Coverage: ✓ Core workflow
```

#### Path 2: Iterative Refinement Path
```
1. User creates project
2. Provides narrative
3. Requests script changes (2 iterations)
4. Approves modified script
5. Edits 2 scene descriptions manually
6. Regenerates 3 frames with feedback
7. Approves remaining frames
8. Regenerates 1 video
9. Approves remaining videos
10. Exports final video
11. Success ✓

Expected Duration: ~70 minutes for 30s video
Test Coverage: ✓ Feedback loops, ✓ Selective regeneration
```

#### Path 3: Error Recovery Path
```
1. User creates project
2. Provides narrative
3. Script generation succeeds
4. Frame generation: 2 frames fail
5. System retries automatically
6. 1 frame still fails
7. User manually retries with modified prompt
8. All frames approved
9. Video generation: 1 video fails due to API limit
10. System queues for later
11. User retries after quota reset
12. Exports final video
13. Success ✓

Expected Duration: Variable (depends on quota reset)
Test Coverage: ✓ Error handling, ✓ Manual retry, ✓ State persistence
```

#### Path 4: Timeline Editing Path
```
1. User creates project
2. Completes workflow through video generation
3. Reviews timeline
4. Reorders scenes (move scene 3 to position 1)
5. Removes scene 4 entirely
6. Adds fade transition between scenes 1-2
7. Re-assembles video
8. Exports final video
9. Success ✓

Expected Duration: ~5 minutes for editing + re-assembly
Test Coverage: ✓ Timeline manipulation, ✓ Re-assembly
```

#### Path 5: Resume After Interruption Path
```
1. User creates project
2. Completes script and scene planning
3. Starts frame generation (3/10 frames complete)
4. CLI crashes or user exits
5. User restarts CLI
6. Runs `nb-studio resume --project <id>`
7. System loads from checkpoint
8. Continues frame generation from frame 4
9. Completes workflow
10. Success ✓

Expected Duration: Normal + 2 minutes overhead
Test Coverage: ✓ State persistence, ✓ Checkpoint recovery
```

### 5.2 Key Test Scenarios

#### Test Suite 1: Unit Tests

**Service Layer Tests:**
```python
# test_claude_service.py
def test_generate_script_from_narrative()
def test_breakdown_script_into_scenes()
def test_generate_frame_prompts_with_style()
def test_ensure_character_consistency()
def test_refine_based_on_feedback()

# test_workflow_service.py
def test_create_workflow_for_project()
def test_advance_to_next_phase()
def test_rollback_to_previous_phase()
def test_checkpoint_saves_state()
def test_resume_from_checkpoint()

# test_frame_service.py
def test_generate_single_frame()
def test_batch_generate_frames()
def test_approve_frame_updates_status()
def test_regenerate_frame_with_feedback()
def test_retry_failed_frame()

# test_assembly_service.py
def test_compile_videos_with_ffmpeg()
def test_add_transitions_between_scenes()
def test_validate_timeline_duration()
def test_export_multiple_formats()
```

**Database Tests:**
```python
# test_database.py
def test_create_project()
def test_store_script_version()
def test_update_workflow_phase()
def test_cascade_delete_project()
def test_concurrent_batch_job_updates()
```

#### Test Suite 2: Integration Tests

**API Integration Tests:**
```python
# test_api_integrations.py
def test_claude_script_generation_end_to_end()
def test_nano_banana_image_generation()
def test_veo3_video_generation_with_reference()
def test_retry_on_api_failure()
def test_rate_limit_handling()
def test_concurrent_api_calls()
```

**Workflow Integration Tests:**
```python
# test_workflow_integration.py
def test_script_to_scenes_pipeline()
def test_scenes_to_frames_pipeline()
def test_frames_to_videos_pipeline()
def test_videos_to_assembly_pipeline()
def test_full_workflow_no_iterations()
def test_full_workflow_with_regenerations()
```

#### Test Suite 3: CLI Tests

**Command Tests:**
```python
# test_cli_commands.py
def test_create_video_command()
def test_resume_command()
def test_show_status_command()
def test_approve_script_command()
def test_regenerate_frame_command()
def test_export_video_command()
def test_help_text_for_all_commands()
```

**Interactive Mode Tests:**
```python
# test_interactive_mode.py
def test_wizard_mode_prompts()
def test_approval_loop_accepts_feedback()
def test_display_frame_grid()
def test_preview_video_opens_player()
```

#### Test Suite 4: End-to-End Tests

**Happy Path Test:**
```python
@pytest.mark.e2e
async def test_complete_workflow_30s_video():
    """
    Test entire workflow from narrative to export
    Duration: ~5 minutes (using mock APIs)
    """
    # 1. Create project
    project = await create_project("Test Video")

    # 2. Generate script
    script = await generate_and_approve_script(project, "A journey through nature")

    # 3. Plan scenes
    scenes = await generate_and_approve_scenes(script)
    assert len(scenes) == 5

    # 4. Generate frames
    frames = await batch_generate_frames(scenes)
    assert all(f.status == "completed" for f in frames)
    await approve_all_frames(frames)

    # 5. Generate videos
    videos = await batch_generate_videos(scenes, frames)
    assert all(v.status == "completed" for v in videos)
    await approve_all_videos(videos)

    # 6. Assemble
    final_video = await assemble_and_export(project, quality="high")

    # Assertions
    assert os.path.exists(final_video)
    assert get_video_duration(final_video) == pytest.approx(30, abs=2)
```

**Error Recovery Test:**
```python
@pytest.mark.e2e
async def test_recovery_from_api_failures():
    """
    Test workflow with simulated API failures and recovery
    """
    project = await create_project("Recovery Test")

    # Simulate frame generation failures
    with mock_api_failures(rate=0.3):  # 30% failure rate
        frames = await batch_generate_frames(project)

    # Some frames should have failed
    failed_frames = [f for f in frames if f.status == "failed"]
    assert len(failed_frames) > 0

    # Retry should succeed
    await retry_failed_frames(failed_frames)
    frames = await get_all_frames(project)
    assert all(f.status == "completed" for f in frames)
```

**State Persistence Test:**
```python
@pytest.mark.e2e
async def test_resume_after_interruption():
    """
    Test that workflow can resume from saved state
    """
    project = await create_project("Interruption Test")
    script = await generate_and_approve_script(project, "Test narrative")
    scenes = await generate_and_approve_scenes(script)

    # Generate 3 out of 10 frames
    frames = await generate_frames_partial(scenes, count=3)

    # Simulate CLI restart
    workflow = await get_workflow(project.id)
    assert workflow.current_phase == "frame_gen"
    assert workflow.checkpoint is not None

    # Resume
    await resume_workflow(project.id)

    # Complete remaining frames
    frames = await continue_frame_generation()
    assert len(frames) == 10
```

### 5.3 Performance Test Scenarios

**Load Test:**
```python
@pytest.mark.performance
async def test_concurrent_project_processing():
    """
    Test system handles multiple concurrent projects
    """
    projects = [await create_project(f"Project {i}") for i in range(5)]

    # Run frame generation for all projects concurrently
    start = time.time()
    results = await asyncio.gather(*[
        batch_generate_frames(p) for p in projects
    ])
    duration = time.time() - start

    # Should complete in reasonable time with concurrency
    assert duration < 15 * 60  # 15 minutes for 5 projects
    assert all(len(r) > 0 for r in results)
```

**Stress Test:**
```python
@pytest.mark.performance
async def test_large_project_60_scenes():
    """
    Test system handles large project (60s video, 12 scenes)
    """
    project = await create_project("Large Project")
    script = await generate_script(project, target_duration=60)
    scenes = await generate_scenes(script)

    assert len(scenes) >= 10  # At least 10 scenes for 60s

    # Should complete without memory issues
    frames = await batch_generate_frames(scenes)
    videos = await batch_generate_videos(scenes, frames)
    final = await assemble_video(project)

    assert os.path.exists(final)
    assert get_video_duration(final) == pytest.approx(60, abs=3)
```

### 5.4 Edge Cases & Boundary Tests

```python
# Edge Case Tests
def test_empty_narrative_handled_gracefully()
def test_single_scene_video()
def test_maximum_duration_limit()  # e.g., 120s
def test_special_characters_in_project_name()
def test_unicode_in_script_content()
def test_regenerate_already_approved_frame()
def test_delete_project_mid_workflow()
def test_concurrent_approval_of_same_frame()
def test_network_timeout_during_generation()
def test_disk_full_during_video_save()
def test_invalid_aspect_ratio_fallback()
def test_missing_reference_frame_for_video()
```

### 5.5 Test Data Requirements

**Test Narratives:**
```
1. Simple: "A sunrise over mountains" (1 scene, 5s)
2. Standard: "A day in the life of a coffee shop" (5 scenes, 30s)
3. Complex: "Journey of a space explorer discovering a new planet" (10 scenes, 60s)
4. Character-heavy: "Two friends having a conversation in a park" (4 scenes, 20s)
```

**Test Style Templates:**
```
1. Cinematic: "dramatic lighting, wide angles, warm color grading"
2. Minimal: "clean, simple, white background, soft lighting"
3. Vibrant: "bright colors, high contrast, energetic"
4. Dark: "moody, low-key lighting, desaturated colors"
```

**Mock API Responses:**
- Pre-generated images for frame tests
- Pre-generated videos for assembly tests
- Claude responses for script variations
- Error responses for failure scenarios

---

## 6. TECHNICAL ARCHITECTURE SUMMARY

### 6.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI LAYER (Typer + Rich)                │
│  Commands: create-video, resume, show-status, approve-*, etc.   │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────────┐
│                    WORKFLOW ORCHESTRATION                        │
│  - State machine (planning → script → scenes → frames → videos) │
│  - Checkpoint & resume logic                                     │
│  - Approval workflow management                                  │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────────┐
│                        SERVICE LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Claude       │  │ Frame        │  │ Video        │          │
│  │ Service      │  │ Service      │  │ Service      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Script       │  │ Scene        │  │ Assembly     │          │
│  │ Service      │  │ Service      │  │ Service      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │ Workflow     │  │ Batch        │  (Reuse existing:          │
│  │ Service      │  │ Service      │   gemini, storage)         │
│  └──────────────┘  └──────────────┘                            │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────────┐
│                     INTEGRATION LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Claude API   │  │ Nano Banana  │  │ Veo3 API     │          │
│  │ (Anthropic)  │  │ (Gemini)     │  │ (Google)     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │ FFmpeg       │  │ Database     │                            │
│  │ (Local)      │  │ (SQLite)     │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Data Flow Diagram

```
User Narrative
     │
     ▼
┌─────────────┐
│ Claude API  │ → Script (structured text)
└─────────────┘
     │
     ▼
┌─────────────┐
│ Scene Parser│ → Scenes (with frame prompts)
└─────────────┘
     │
     ▼
┌─────────────┐
│ Nano Banana │ → Images (key frames)
└─────────────┘
     │
     ▼
┌─────────────┐
│ Veo3 API    │ → Videos (per scene)
└─────────────┘
     │
     ▼
┌─────────────┐
│ FFmpeg      │ → Final Video (compiled)
└─────────────┘
```

### 6.3 File Structure

```
nano-banana-image-studio/
├── backend/
│   ├── src/
│   │   ├── cli/                     # NEW: CLI application
│   │   │   ├── __init__.py
│   │   │   ├── main.py              # Typer app entry point
│   │   │   ├── commands/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── project.py       # create-video, list, delete
│   │   │   │   ├── script.py        # show-script, approve-script
│   │   │   │   ├── scenes.py        # show-scenes, edit-scene
│   │   │   │   ├── frames.py        # show-frames, approve-frame, regenerate
│   │   │   │   ├── videos.py        # show-videos, approve-video
│   │   │   │   └── export.py        # export-video
│   │   │   ├── ui/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── display.py       # Rich formatting utilities
│   │   │   │   ├── prompts.py       # Interactive prompts
│   │   │   │   └── progress.py      # Progress bars
│   │   │   └── utils/
│   │   │       ├── __init__.py
│   │   │       └── validation.py    # Input validation
│   │   ├── services/                # EXTEND: Add new services
│   │   │   ├── gemini.py            # (existing)
│   │   │   ├── storage.py           # (existing)
│   │   │   ├── claude_service.py    # NEW
│   │   │   ├── script_service.py    # NEW
│   │   │   ├── scene_service.py     # NEW
│   │   │   ├── frame_service.py     # NEW
│   │   │   ├── video_service.py     # NEW (extend existing)
│   │   │   ├── assembly_service.py  # NEW
│   │   │   ├── workflow_service.py  # NEW
│   │   │   └── batch_service.py     # NEW
│   │   ├── models.py                # EXTEND: Add new Pydantic models
│   │   ├── database.py              # EXTEND: Add new tables
│   │   └── config.py                # EXTEND: Add CLI config
│   └── tests/                       # NEW: Test suite
│       ├── unit/
│       │   ├── test_claude_service.py
│       │   ├── test_workflow_service.py
│       │   └── ...
│       ├── integration/
│       │   ├── test_api_integrations.py
│       │   └── test_workflow_integration.py
│       ├── e2e/
│       │   ├── test_happy_path.py
│       │   └── test_error_recovery.py
│       └── fixtures/
│           ├── narratives.json
│           └── mock_responses/
├── docs/                            # NEW: Documentation
│   ├── video-production-cli-requirements.md  # THIS FILE
│   ├── cli-user-guide.md            # User manual
│   └── api-integration-guide.md     # API setup guide
├── projects/                        # NEW: User project workspaces
│   └── <project-id>/
│       ├── project.json
│       ├── script.md
│       ├── scenes.json
│       ├── frames/
│       ├── videos/
│       ├── output/
│       └── logs/
└── README.md                        # UPDATE: Add CLI instructions
```

---

## 7. IMPLEMENTATION ROADMAP (HIGH-LEVEL)

### Phase 1: Foundation (Week 1-2)
- Set up CLI framework with Typer + Rich
- Extend database schema with new tables
- Create basic project management (create, list, delete)
- Implement workflow state machine

### Phase 2: Script Generation (Week 3)
- Integrate Claude API for script generation
- Build conversational feedback loop
- Implement script versioning
- Create scene breakdown parser

### Phase 3: Frame Generation (Week 4-5)
- Build frame generation workflow
- Implement batch processing with queue
- Create approval/review UI in CLI
- Add regeneration with feedback

### Phase 4: Video Generation (Week 6-7)
- Integrate Veo3 API (or mock if unavailable)
- Implement reference frame support
- Build video review workflow
- Add trimming capabilities

### Phase 5: Assembly & Export (Week 8)
- Integrate FFmpeg for compilation
- Implement transition support
- Build export with quality presets
- Add timeline editing

### Phase 6: Polish & Testing (Week 9-10)
- Comprehensive test coverage
- Error handling refinement
- Performance optimization
- Documentation and user guide

---

## 8. SUCCESS METRICS

### 8.1 Quantitative Metrics
- **Time to First Video**: < 60 minutes for new users
- **Script Approval Rate**: > 80% on first generation
- **Frame Approval Rate**: > 70% on first generation
- **Video Approval Rate**: > 60% on first generation
- **API Success Rate**: > 95% after retries
- **User Retention**: > 50% create second video

### 8.2 Qualitative Metrics
- User reports CLI is "intuitive" or "easy to use"
- Visual consistency rated 4/5 or higher
- Users prefer CLI over manual editing for short-form content
- Positive feedback on Claude integration quality

### 8.3 Technical Metrics
- < 5% error rate in production
- < 2 second CLI startup time
- 99% state persistence success
- Zero data loss incidents

---

## 9. RISKS & MITIGATIONS

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Veo3 API not available/affordable | High | Medium | Build with mock mode, support alternatives (Runway, Pika) |
| Claude token costs too high | Medium | Medium | Implement caching, optimize prompts, add token budgets |
| Inconsistent character generation | High | High | Use reference images, character templates, multiple retries |
| FFmpeg compatibility issues | Low | Low | Test across platforms, provide installation guide |
| User abandonment mid-workflow | Medium | Medium | Auto-save, clear checkpoints, easy resume |
| API rate limits block workflow | High | Medium | Queue system, graceful degradation, user notifications |

---

## 10. OPEN QUESTIONS

1. **Character Consistency**: What additional techniques beyond reference images can ensure character consistency? (e.g., LoRA models, controlnet)

2. **Video Transitions**: Should we support advanced transitions (crossfade, wipe) or keep simple cuts?

3. **Audio**: Should we support background music or voiceover in v1, or defer to v2?

4. **Pricing**: How do we communicate API costs to users? Real-time cost tracking?

5. **Collaboration**: Should multiple users be able to work on same project? (Future feature)

6. **Alternative APIs**: Priority order for supporting Runway, Pika, Stability AI as alternatives?

7. **Export Formats**: Which formats beyond MP4 are essential? (MOV, WebM, GIF)

8. **Batch Limits**: What's the maximum number of scenes/frames we should support?

---

## APPENDIX A: CLI Command Reference (Proposed)

```bash
# Project Management
nb-studio create-video [--name NAME] [--wizard]
nb-studio list-projects [--status STATUS]
nb-studio show-project <project-id>
nb-studio delete-project <project-id>
nb-studio resume <project-id>

# Script Phase
nb-studio generate-script <project-id> --narrative "..."
nb-studio show-script <project-id>
nb-studio approve-script <project-id>
nb-studio edit-script <project-id>  # Opens in editor

# Scene Phase
nb-studio show-scenes <project-id>
nb-studio edit-scene <project-id> <scene-number>
nb-studio approve-scenes <project-id>

# Frame Phase
nb-studio generate-frames <project-id>
nb-studio show-frames <project-id> [--scene SCENE]
nb-studio review-frame <project-id> <frame-id>
nb-studio approve-frame <project-id> <frame-id>
nb-studio approve-all-frames <project-id>
nb-studio regenerate-frame <project-id> <frame-id> [--feedback "..."]
nb-studio regenerate-all-frames <project-id>

# Video Phase
nb-studio generate-videos <project-id>
nb-studio show-videos <project-id>
nb-studio play-video <project-id> <scene-number>
nb-studio approve-video <project-id> <scene-video-id>
nb-studio approve-all-videos <project-id>
nb-studio regenerate-video <project-id> <scene-video-id> [--prompt "..."]
nb-studio trim-video <project-id> <scene-video-id> --start 0.5 --end 4.5

# Assembly Phase
nb-studio show-timeline <project-id>
nb-studio move-scene <project-id> <from> <to>
nb-studio remove-scene <project-id> <scene-number>
nb-studio add-transition <project-id> <scene-1> <scene-2> --type fade
nb-studio export-video <project-id> [--format mp4] [--quality high] [--output PATH]

# Utilities
nb-studio config [--set KEY=VALUE]
nb-studio templates list [--category CATEGORY]
nb-studio templates create --name NAME --style "..."
nb-studio logs <project-id> [--tail N]
```

---

## APPENDIX B: Configuration File Schema

```yaml
# ~/.nb-studio/config.yaml
api_keys:
  anthropic: "sk-ant-..."
  google_gemini: "..."
  google_veo: "..."

defaults:
  aspect_ratio: "16:9"
  video_duration: 30
  image_model: "gemini-2.5-flash-image"
  video_model: "veo-3.0-generate-preview"
  style: "cinematic"
  quality: "high"

cli:
  mode: "wizard"  # or "expert"
  show_emojis: true
  color_scheme: "default"
  auto_open_previews: true

workflow:
  auto_save: true
  checkpoint_frequency: "every_step"  # or "every_phase"
  retry_attempts: 3
  retry_backoff: 2

batch:
  max_concurrent_frames: 5
  max_concurrent_videos: 2

paths:
  projects_dir: "./projects"
  output_dir: "./outputs"
  logs_dir: "./logs"
```

---

**END OF REQUIREMENTS DOCUMENT**

This document serves as the comprehensive blueprint for implementing the Video Production CLI for Nano Banana Image Studio. All stakeholders should review and approve before development begins.
