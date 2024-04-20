# InvalidSignatureException

## Error:
```
botocore.exceptions.ClientError: An error occurred (InvalidSignatureException) when calling the SendEmail operation: The request signature we calculated does not match the signature you provided. Check your AWS Secret Access Key and signing method. Consult the service documentation for details.
```

## Solution

Keep regenerating IAM Access Keys until the SECRET KEY doesn't contain a **slash** (/) or a **plus** (+)
