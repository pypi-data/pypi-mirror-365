# BACnet Management Feature Summary

## Overview

This feature branch adds BACnet management capabilities to the aceiot-models-cli tool. The feature allows users to control BACnet functionality on gateways by manipulating semaphore values in the gateway's `deploy_config` structure.

## New Commands

All commands are under the `gateways` command group:

### 1. `aceiot gateways trigger-scan <gateway_name>`
- Triggers a BACnet scan on the specified gateway
- Sets `deploy_config.trigger_scan` to `true`
- Optional: `--scan-address` to update the scan network address
- Example: `aceiot gateways trigger-scan my-gateway --scan-address 192.168.1.0/24`

### 2. `aceiot gateways deploy-points <gateway_name>`
- Triggers point deployment to the gateway
- Sets `deploy_config.trigger_deploy` to `true`
- Example: `aceiot gateways deploy-points my-gateway`

### 3. `aceiot gateways enable-bacnet <gateway_name>`
- Enables BACnet on the gateway
- Sets `deploy_config.deploy_bacnet` to `true`
- Example: `aceiot gateways enable-bacnet my-gateway`

### 4. `aceiot gateways disable-bacnet <gateway_name>`
- Disables BACnet on the gateway
- Sets `deploy_config.deploy_bacnet` to `false`
- Example: `aceiot gateways disable-bacnet my-gateway`

### 5. `aceiot gateways bacnet-status <gateway_name>`
- Shows current BACnet configuration status
- Displays all BACnet-related settings and timestamps
- Supports `-o json` for JSON output
- Example: `aceiot gateways bacnet-status my-gateway -o json`

## REPL Support

The BACnet commands are fully integrated with the REPL mode with context-aware features:

### Direct BACnet Commands in Gateway Context
When in a gateway context, BACnet commands can be used directly without the 'gateways' prefix:

```bash
aceiot repl
aceiot> use gateway my-gateway
aceiot(gw:my-gateway)> trigger-scan
# Automatically uses 'my-gateway' as the target

aceiot(gw:my-gateway)> deploy-points
# Direct command execution

aceiot(gw:my-gateway)> bacnet-status -o json
# Works with options too
```

You can still use the full 'gateways <command>' form if needed for clarity or scripting.

### Context-Aware Help
The help system now shows relevant BACnet commands when in gateway context:

```bash
aceiot(gw:my-gateway)> help

Gateway Context Commands:
  get                    Get current gateway details
  trigger-scan           Trigger BACnet scan on current gateway
  deploy-points          Deploy points to current gateway
  enable-bacnet          Enable BACnet on current gateway
  disable-bacnet         Disable BACnet on current gateway
  bacnet-status          Show BACnet configuration status

BACnet Examples:
  trigger-scan --scan-address 192.168.1.0/24
  bacnet-status -o json
  deploy-points
```

## Implementation Details

### Files Added
- `src/aceiot_models_cli/bacnet_commands.py` - Core BACnet command implementations
- `tests/test_bacnet_commands.py` - Tests for BACnet commands
- `tests/test_repl_bacnet_commands.py` - Tests for REPL BACnet functionality
- `tests/test_repl_context_help.py` - Tests for context-aware help system
- `tests/test_repl_direct_bacnet_commands.py` - Tests for direct BACnet commands in gateway context

### Files Modified
- `src/aceiot_models_cli/cli.py` - Added BACnet commands to gateway group
- `src/aceiot_models_cli/repl/executor.py` - Added REPL context support for BACnet commands, direct command execution, and context-aware help
- `src/aceiot_models_cli/repl/parser.py` - Updated to recognize BACnet commands as REPL commands in gateway context

### API Integration
- Uses `APIClient.patch_gateway()` to update gateway configuration
- Properly handles API errors and provides detailed error messages
- Preserves existing deploy_config values while updating only the necessary fields

## Testing

Comprehensive test coverage includes:
- All command functionality with various options
- Error handling scenarios
- REPL context integration
- Explicit gateway name override in REPL mode

All tests pass with no regressions to existing functionality.

## Usage Examples

### CLI Mode
```bash
# Enable BACnet and trigger a scan
aceiot gateways enable-bacnet gateway-001
aceiot gateways trigger-scan gateway-001 --scan-address 192.168.10.0/24

# Check status
aceiot gateways bacnet-status gateway-001

# Deploy points when ready
aceiot gateways deploy-points gateway-001
```

### REPL Mode with Direct Commands
```bash
aceiot repl
aceiot> use gateway gateway-001
aceiot(gw:gateway-001)> bacnet-status
aceiot(gw:gateway-001)> trigger-scan --scan-address 192.168.10.0/24
aceiot(gw:gateway-001)> deploy-points
aceiot(gw:gateway-001)> help  # Shows context-aware help
```

## Next Steps

1. Merge this feature branch to main
2. Consider adding:
   - Progress monitoring for scan/deploy operations
   - Bulk operations for multiple gateways
   - Scan result viewing capabilities
   - Point deployment verification