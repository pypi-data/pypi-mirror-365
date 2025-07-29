# Must CDK

A collection of AWS CDK constructs that implement common architectural patterns and best practices for AWS services. This library aims to simplify the deployment of common cloud infrastructure patterns while maintaining security, scalability, and operational excellence.

## Features

### 🏗️ Amplify Patterns

* Next.js application deployment optimizations
* Multi-environment branch configurations
* Custom domain and SSL setup
* GitHub personal access token authentication
* Automated build and deployment pipelines
* Migration path to GitHub Apps for production
* CLI tool for quick project initialization

### 🚢 ECS CodeDeploy Patterns

* Blue/Green deployment strategies
* Load balanced service deployments
* Auto-scaling configurations
* Health check implementations
* Container security best practices

### 🌐 CloudFront Patterns

* API Gateway integrations
* Multi-origin configurations
* Cross-region setups
* Security headers and WAF integration
* Caching strategies
* Custom domain configurations

### 🔌 API Gateway Lambda Patterns

* REST API implementations
* WebSocket API setups
* Custom domain configurations
* Lambda authorizers
* Rate limiting and API key management

## Installation

### TypeScript/JavaScript

```bash
npm install must-cdk
# or
yarn add must-cdk
```

### Python

```bash
pip install must-cdk
```

### CLI Tool

Install globally to quickly initialize Amplify projects:

```bash
# Install CLI globally
npm install -g must-cdk

# Initialize Amplify project with React template
must-cdk amplify init

# Initialize in specific directory
must-cdk amplify init -d /path/to/project
```

## 🏷️ Tags Management

Must CDK provides a unified tagging system that automatically applies tags to all resources across all constructs. This system supports both environment-based tags and construct-specific tags.

### Environment Tags

Set tags globally using the `TAGS` environment variable:

```bash
# Format: key1=value1,key2=value2
export TAGS="Product=MyApp,Owner=TeamName,Environment=production,CostCenter=engineering"

# Deploy with environment tags
cdk deploy
```

### Construct-Specific Tags

Add tags directly to individual constructs:

```python
// TypeScript
new AmplifyApp(this, 'MyApp', {
  appName: 'my-application',
  repository: 'https://github.com/user/repo',
  tags: {
    Team: 'frontend',
    Version: 'v1.0.0',
    Component: 'web-app'
  }
});
```

```python
# Python
AmplifyApp(self, 'MyApp',
  app_name='my-application',
  repository='https://github.com/user/repo',
  tags={
    'Team': 'frontend',
    'Version': 'v1.0.0',
    'Component': 'web-app'
  }
)
```

### Tag Precedence

Environment tags take precedence over construct-specific tags:

```bash
# Environment variable
export TAGS="Environment=production,Team=platform"

# In your code
tags: {
  Team: 'frontend',      # Will be overridden by environment
  Component: 'web-app'   # Will be preserved
}

# Final tags applied:
# Environment=production (from env)
# Team=platform (from env, overrides construct tag)
# Component=web-app (from construct)
```

### Supported Constructs

All Must CDK constructs support the tagging system:

* **AmplifyApp**: Tags applied to Amplify app and branches
* **CloudFrontToOrigins**: Tags applied to CloudFront distribution and related resources
* **ApiGatewayToLambda**: Tags applied to API Gateway and Lambda resources
* **WebSocketApiGatewayToLambda**: Tags applied to WebSocket API and Lambda resources
* **EcsCodeDeploy**: Tags applied to ECS services, task definitions, and load balancers

### Advanced Tag Examples

```bash
# Complex environment tags with special characters
export TAGS="Product=MyApp,URL=https://api.example.com/v1,Config=key1=val1&key2=val2"

# Multi-environment setup
export TAGS="Product=MyApp,Environment=staging,Owner=DevTeam"  # Staging
export TAGS="Product=MyApp,Environment=production,Owner=OpsTeam"  # Production
```

### Best Practices

1. **Consistent Naming**: Use consistent tag keys across all environments
2. **Environment Separation**: Use different tag values for different environments
3. **Cost Tracking**: Include cost center and project tags for billing
4. **Automation**: Set environment tags in CI/CD pipelines
5. **Documentation**: Document your tagging strategy for the team

```bash
# Recommended tag structure
export TAGS="Product=MyProduct,Environment=production,Owner=TeamName,CostCenter=Engineering,Project=WebApp"
```

## Documentation

Detailed documentation for each construct can be found in:

* [Python API Reference](./docs/python/api.md)
* [Tags Documentation](./docs/TAGS.md)
* [Examples](./examples/README.md)

## Examples

The [examples](./examples) directory contains working examples for each construct category:

* Amplify deployment patterns
* ECS with CodeDeploy configurations
* CloudFront distribution setups
* API Gateway with Lambda integrations

Each example is provided in both TypeScript and Python with detailed comments and instructions.
