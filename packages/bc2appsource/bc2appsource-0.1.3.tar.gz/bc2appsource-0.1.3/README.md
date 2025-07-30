# BC2AppSource

A Python package for publishing Business Central apps to Microsoft AppSource.

## Installation

```bash
pip install bc2appsource
```

## Usage

### Command Line Interface

```bash
# Publish an app to AppSource
bc2appsource publish \
  --app-file path/to/your/app.app \
  --tenant-id your-tenant-id \
  --client-id your-client-id \
  --client-secret your-client-secret \
  --product-name "Your Product Name"

# With library app file
bc2appsource publish \
  --app-file path/to/your/app.app \
  --library-app-file path/to/library.app \
  --tenant-id your-tenant-id \
  --client-id your-client-id \
  --client-secret your-client-secret \
  --product-name "Your Product Name"
```

### Python API

```python
from bc2appsource import AppSourcePublisher

publisher = AppSourcePublisher(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Publish app
result = publisher.publish(
    app_file="path/to/your/app.app",
    product_name="Your Product Name",
    library_app_file="path/to/library.app",  # Optional
    auto_promote=True
)

if result.success:
    print(f"Submission ID: {result.submission_id}")
else:
    print(f"Error: {result.error}")
```

## Authentication

You need to register an Azure AD application with the following permissions:
- Microsoft Partner Center API access
- Application permissions for submitting to AppSource

## Environment Variables

You can also use environment variables instead of passing credentials:

```bash
export AZURE_TENANT_ID=your-tenant-id
export AZURE_CLIENT_ID=your-client-id
export AZURE_CLIENT_SECRET=your-client-secret
```

## GitHub Actions

This package can be used in GitHub Actions workflows:

```yaml
- name: Install bc2appsource
  run: pip install bc2appsource

- name: Publish to AppSource
  run: |
    bc2appsource publish \
      --app-file artifacts/*.app \
      --product-name "${{ github.event.repository.name }}"
  env:
    AZURE_TENANT_ID: ${{ secrets.APPSOURCE_TENANT_ID }}
    AZURE_CLIENT_ID: ${{ secrets.APPSOURCE_CLIENT_ID }}
    AZURE_CLIENT_SECRET: ${{ secrets.APPSOURCE_CLIENT_SECRET }}
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
