# BLACK VECTOR Phase 0 — Precise Execution Plan

## Purpose
Phase 0 Foundation and Environment Verification for BLACK VECTOR multiplayer FPS game

## Goal
Verify Unreal Engine 5 environment, establish project baseline, and prepare for Phase 1 gameplay implementation

## Current Status Assessment
**Phase 0 is NOT_STARTED** - Blocked on environment inspection

## Required Documents (Already Available)
- ✅ Docs/GAME_BIBLE.md (Product specification and locked decisions)
- ✅ Docs/ROADMAP.md (Development roadmap)
- ✅ Docs/ARCHITECTURE.md (Technical architecture)
- ✅ Docs/PHASE0_CHECKLIST.md (Verification checklist)
- ✅ Docs/TASKS.md (Task board with current status)

## Phase 0 Tasks & Implementation Priorities

### A. Environment Inspection (P0-T01/P0-T02/P0-T03)

**P0-T01 - Repository and tooling baseline**
- Verify: `uv sync --frozen --all-groups`
- Verify: `ruff check .`
- Verify: `mypy --strict app tests`
- **Status**: Ready to implement
- **Evidence required**: Toolchain verification output

**P0-T02 - FastAPI skeleton and configuration**
- Verify: Application boots and `/health/live` responds 200
- **Status**: COMPLETED in session 2 (per PROJECT_STATUS.md)
- **Implementation**: FastAPI main/config/logging modules exist

**P0-T03 - PostgreSQL 16 provisioning and hardening**
- Verify: Local PostgreSQL 16.16 available
- Verify: pgAudit runtime enabled
- Verify: Hardening assertions pass
- **Status**: READY_FOR_REVIEW (per PROJECT_STATUS.md)
- **Blocker**: CI workflow still pending (§15)

### B. Unreal Engine 5 Environment (NEW TASKS)

**P0-T04 - Unreal Engine 5 environment inspection**
- **Objective**: Confirm exact UE5 version and build toolchain
- **Implementation**:
  1. Inspect local workspace for existing Unreal project
  2. Detect UE5 installation path and version
  3. Verify Visual Studio/MSVC C++ toolchain
  4. Confirm Windows SDK versions
  5. Record hardware specs and disk space
  6. Update Docs/ENVIRONMENT.md with findings

**P0-T05 - Unreal project creation/verification**
- **Objective**: Create or inspect C++ Unreal project
- **Implementation**:
  1. Choose project root directory
  2. Create new UE5 C++ project OR inspect existing
  3. Generate project files
  4. Build Development Editor target
  5. Launch project and inspect logs
  6. Confirm clean baseline commit to Git

**P0-T06 - Dedicated server feasibility**
- **Objective**: Verify server build path for selected UE5 version
- **Implementation**:
  1. Confirm UE5 supports intended server workflow
  2. Review server target requirements
  3. Create minimal server target
  4. Build server target
  5. Run local server and connect test client
  6. Record limitations/constraints

### C. Git Repository Baseline (P0-T07/P0-T08)

**P0-T07 - Git initialization and documentation**
- **Objective**: Initialize Git with Unreal-appropriate .gitignore
- **Implementation**:
  1. Initialize Git repository
  2. Create Unreal-specific .gitignore
  3. Commit documentation baseline
  4. Configure remote repository

**P0-T08 - Phase 0 exit review**
- **Objective**: Verify all exit criteria met
- **Implementation**:
  1. Confirm editor target builds and launches
  2. Confirm repository cleanly initialized
  3. Confirm environment documented
  4. Confirm server build path verified
  5. Record any blockers precisely

## Exit Criteria for Phase 0

**VERIFIED when ALL of the following are met:**
1. ✅ Development Editor target builds and launches successfully
2. ✅ Repository cleanly initialized with proper baseline
3. ✅ Development environment fully documented (Docs/ENVIRONMENT.md)
4. ✅ Dedicated server build path confirmed or precise blocker recorded
5. ✅ All Phase 0 tasks marked COMPLETED with evidence
6. ✅ No unresolved critical errors in build/test logs

**BLOCKED when ANY of the following exist:**
- Unreal Engine 5 not available or incompatible
- Unable to create/inspect Unreal project
- Editor build fails
- Server build path cannot be verified
- Git repository cannot be initialized
- Critical environment constraints preventing progress

## Implementation Timeline

**Week 1 (Current)**: Environment inspection and setup
**Week 2**: Unreal project creation and verification
**Week 3**: Server feasibility testing
**Week 4**: Git baseline and exit review

## Verification Requirements

**For each task:**
- Record exact commands executed
- Capture command output as evidence
- Update relevant documentation files
- Document any blockers with precise reasons
- Do not mark task VERIFIED without evidence

**Final verification:**
- Run all Phase 0 verification commands
- Review documentation updates
- Confirm exit criteria satisfied
- Produce final verification report

## Immediate Next Actions

**Priority 1 - Environment Setup:**
1. Execute toolchain verification commands
2. Verify existing FastAPI application
3. Check PostgreSQL availability

**Priority 2 - Unreal Inspection:**
1. Detect Unreal Engine 5 installation
2. Check for existing Unreal project
3. Prepare project creation steps

**Priority 3 - Documentation:**
1. Update Docs/ENVIRONMENT.md baseline
2. Create initial Git .gitignore
3. Establish documentation structure

## Risk Mitigation

**High Risk Items:**
- Unreal Engine 5 not installed: Alternative development environment needed
- Windows SDK incompatibility: Toolchain updates required
- Disk space constraints: Project relocation or cleanup

**Medium Risk Items:**
- Server build limitations: May require UE5 version adjustment
- Git repository conflicts: Need clean workspace state
- Documentation inconsistencies: Requires careful alignment

## Success Metrics

**Technical Metrics:**
- Engine version: Exact UE5 minor version verified
- Build success: Editor and server targets build cleanly
- Environment: All dependencies and toolchains confirmed
- Repository: Clean, documented Git baseline established

**Documentation Metrics:**
- Environment: Comprehensive Docs/ENVIRONMENT.md
- Tasks: All Phase 0 tasks tracked and evidenced
- Blocker: Precise blocker documentation when exists
- Exit: Clear Phase 0 exit criteria verification

## Command Execution Plan

**Toolchain verification commands:**
```powershell
uv sync --frozen --all-groups
ruff check .
mypy --strict app tests
```

**Application verification:**
```powershell
# FastAPI application verification
# (Commands will be executed in development environment)
```

**Unreal environment commands:**
```powershell
# Unreal Engine 5 detection commands
# (Commands will be executed in development environment)
```

**Git repository commands:**
```powershell
# Git initialization and baseline establishment
# (Commands will be executed in development environment)
```

This plan is implementation-ready and can be executed immediately. All tasks are clearly defined with evidence requirements and exit criteria.