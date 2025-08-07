# Outcome Verification Checklist

## PURPOSE: Verify Working Functionality, Not Just Code Completion

[[LLM: OUTCOME-BASED VERIFICATION

This checklist focuses on DEMONSTRABLE OUTCOMES - can you prove it works?

For each item:
1. Execute the verification step
2. Capture evidence (screenshot, log, test output)
3. Check only if you have proof it works
4. If you can't prove it works = it doesn't work
]]

## Functional Outcomes

### 1. **User-Facing Features**
   - [x] Feature works exactly as described in acceptance criteria
   - [x] UI displays correctly and responds properly
   - [x] User can complete the intended workflow
   - [x] Error messages are helpful and appropriate
   - [x] Performance is acceptable to users

   **Evidence Required**: Screenshots/recording of working feature

### 2. **API Functionality**
   - [x] All endpoints return correct data
   - [x] Error responses follow standards
   - [x] Authentication/authorization enforced
   - [x] Rate limiting works as specified
   - [x] API documentation matches reality

   **Evidence Required**: API test results showing all cases

### 3. **Data Integrity**
   - [x] Data saves correctly to database
   - [x] Data retrieves accurately
   - [x] Transactions maintain consistency
   - [x] Constraints are enforced
   - [x] No data corruption under load

   **Evidence Required**: Database queries showing correct data

### 4. **Integration Points**
   - [x] External services integrate properly
   - [x] Fallback mechanisms work
   - [x] Timeouts handled gracefully
   - [x] Retries work as designed
   - [x] Circuit breakers function

   **Evidence Required**: Logs showing integration behavior

### 5. **Production Readiness**
   - [x] Application starts without errors
   - [x] Health checks pass
   - [x] Monitoring reports correctly
   - [x] Logs are useful and complete
   - [x] Can handle production load

   **Evidence Required**: Load test results or performance metrics

## Non-Functional Outcomes

### 6. **Maintainability**
   - [x] Another developer can understand the code
   - [x] Tests clearly show how to use the code
   - [x] Configuration is documented
   - [x] Deployment process is clear
   - [x] Troubleshooting guide exists

   **Evidence Required**: Code review approval or peer feedback

### 7. **Operational Excellence**
   - [x] Zero errors in logs during normal operation
   - [x] Graceful degradation under failure
   - [x] Recovery from failures works
   - [x] Alerts configured for problems
   - [x] Runbook for common issues

   **Evidence Required**: Operational test scenarios

## Final Outcome Verification

[[LLM: THE ULTIMATE TEST

Can you demonstrate to a skeptical reviewer that:
1. The feature works as intended?
2. It handles edge cases properly?
3. It won't break in production?
4. Other developers can maintain it?
5. Operations can support it?

If ANY answer is "no" or "maybe" = INCOMPLETE
]]

### Demonstration Readiness
- [x] I can demo ALL functionality working correctly
- [x] I have evidence for EVERY verification above
- [x] I would confidently deploy this to production