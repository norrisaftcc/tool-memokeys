# Multi-Agent Development Workflow Template

## Overview
This document defines the optimized workflow for coordinating multiple specialized AI agents in software development projects, developed during the MemoKeys Swift MVP project.

## Agent Roles & Responsibilities

### 🏃‍♂️ Scrum-Project-Manager
**When to Use**: Sprint planning, backlog organization, process optimization
- Creates and manages sprint backlogs
- Sets up GitHub milestones and labels
- Defines acceptance criteria and story point estimates
- Optimizes agent coordination workflows
- Provides project status and progress tracking

### 👨‍💻 Scrum-Team-Engineer  
**When to Use**: Feature development, code implementation, technical decisions
- Breaks down features into technical tasks
- Implements code changes and new features
- Reviews pull requests and provides technical guidance
- Makes architectural decisions
- Estimates implementation complexity

### 🧪 Test-Engineer
**When to Use**: Quality assurance, test planning, validation
- Creates test strategies and test cases
- Performs manual and automated testing
- Validates feature functionality and edge cases
- Tests cross-platform compatibility
- Provides quality gates for releases

### ✅ Product-Acceptance-Tester
**When to Use**: User experience validation, final approval, process improvement
- Tests from end-user perspective
- Validates features meet requirements
- Conducts usability testing
- Provides final sign-off for releases
- **NEW**: Evaluates agent coordination effectiveness

## Workflow Protocol

### Phase-Based Handoff Pattern
```
Planning → Development → Testing → Acceptance → Done
    ↓           ↓          ↓          ↓
Scrum-PM → Scrum-Engineer → Test-Engineer → Product-Tester
```

### Communication Standards

#### 1. Issue Handoff Comments
When transitioning between agents, use structured comments:

```markdown
## 🔄 Handoff to @[agent-type]

**Completed**: [What was accomplished]
**Status**: [Current state]
**Next Steps**: [What needs to happen next]
**Files Changed**: [List of modified files]
**Testing Notes**: [Any special considerations]

Ready for [next phase].
```

#### 2. Agent Tagging System
- Use GitHub labels to track which agent is responsible
- Add `Status::` labels to show current phase
- Use milestones to group sprint work

#### 3. Status Labels
- `Status::Planning` - In scrum-project-manager phase
- `Status::In-Progress` - Being developed by scrum-team-engineer
- `Status::Testing` - Under review by test-engineer
- `Status::Acceptance` - Being validated by product-acceptance-tester
- `Status::Done` - Completed and approved

## Agent Coordination Best Practices

### 1. Clear Handoff Triggers
Each phase has specific completion criteria:
- **Planning → Development**: Acceptance criteria defined, story pointed
- **Development → Testing**: Code implemented, PR created
- **Testing → Acceptance**: Tests pass, quality gates met
- **Acceptance → Done**: User requirements validated, approved for release

### 2. Structured Deliverables
Each agent provides standardized outputs:
- **Scrum-PM**: Sprint plan, acceptance criteria, estimates
- **Scrum-Engineer**: Working code, technical documentation, PR
- **Test-Engineer**: Test results, bug reports, quality assessment
- **Product-Tester**: UX validation, approval status, improvement recommendations

### 3. Parallel Work Streams
When possible, agents work in parallel:
- Test-Engineer prepares test cases while Scrum-Engineer develops
- Product-Tester reviews requirements while development happens
- Multiple issues can be in different phases simultaneously

## Sprint Execution Template

### Sprint Planning (Scrum-Project-Manager)
1. Review backlog and prioritize issues
2. Create acceptance criteria for each issue
3. Assign story points and estimates
4. Set up milestones and labels
5. Define sprint goals and timeline

### Development Phase (Scrum-Team-Engineer)
1. Break down issues into technical tasks
2. Implement features according to acceptance criteria
3. Create pull requests with clear descriptions
4. Update issue status and provide handoff notes
5. Request testing when implementation complete

### Testing Phase (Test-Engineer)
1. Review acceptance criteria and implementation
2. Create and execute test cases
3. Validate functionality and edge cases
4. Report any bugs or quality issues
5. Approve for acceptance testing when quality gates met

### Acceptance Phase (Product-Acceptance-Tester)
1. Test from end-user perspective
2. Validate against original requirements
3. Conduct usability assessment
4. Provide final approval or request changes
5. Document lessons learned and process improvements

## Success Metrics

### Efficiency Metrics
- **Handoff Time**: < 2 hours between agent transitions
- **Cycle Time**: Total time from issue creation to completion
- **Rework Rate**: Percentage of issues requiring significant changes

### Quality Metrics
- **Bug Escape Rate**: Bugs found after acceptance testing
- **Test Coverage**: Percentage of features with comprehensive tests
- **User Satisfaction**: Product-tester approval rate

### Process Metrics
- **Communication Clarity**: Structured comments usage rate
- **Protocol Adherence**: Percentage following defined handoff process
- **Agent Coordination**: Smooth transitions without delays

## Template Usage

### For New Projects:
1. Copy this workflow template
2. Adapt agent roles to project needs
3. Customize labels and milestones
4. Define project-specific acceptance criteria
5. Train team on handoff protocols

### For Ongoing Projects:
1. Review current agent coordination effectiveness
2. Identify bottlenecks in handoff process
3. Implement improvements to communication patterns
4. Measure and optimize cycle times

## Lessons Learned (MemoKeys Case Study)

### What Worked Well:
- Clear agent specialization improved focus
- Structured handoffs reduced confusion
- Parallel work streams increased velocity
- GitHub integration provided transparency

### Areas for Improvement:
- Initial setup overhead for labels/milestones
- Need for better async communication patterns
- Agent context retention between handoffs
- Standardized deliverable formats

### Recommendations:
- Invest in upfront workflow setup
- Use structured communication templates
- Maintain shared context documents
- Regular retrospectives on agent coordination

---

**Version**: 1.0  
**Created**: 2025-08-15  
**Project**: MemoKeys Swift MVP  
**Status**: Active Template