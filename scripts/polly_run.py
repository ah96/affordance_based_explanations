#!/usr/bin/env python3
"""
Speech demo with AWS Polly, without ROS.

Synthesizes a text with the Amazon Polly service and saves it as
``output.mp3``.  The pitch is set with the SSML tag ``<prosody pitch=...>``.

Prerequisites
-------------
1. An AWS account with access to Polly.
2. AWS credentials (``~/.aws/credentials`` or environment variables).
3. ``pip install boto3``

Usage
-----
    python3 polly_run.py
"""

import boto3

# AWS region where the Polly endpoint is located.
# Change to the region closest to your deployment for lower latency.
AWS_REGION = 'us-west-2'

# Polly voice: 'Joanna' (US English female).  Other options: 'Matthew', 'Amy', 'Brian'.
VOICE_ID = 'Joanna'

# Text to synthesize.  Replace it with a textual explanation of verbalize.py.
TEXT_SSML = (
    '<speak>'
    '<prosody pitch="+20%">'
    'Hello, this is a test with a higher pitch.'
    '</prosody>'
    '</speak>'
)

# Initialise the Polly client using credentials from the default AWS profile.
polly_client = boto3.client('polly', region_name=AWS_REGION)

# Request speech synthesis; TextType='ssml' enables SSML prosody tags.
response = polly_client.synthesize_speech(
    VoiceId=VOICE_ID,
    OutputFormat='mp3',
    Text=TEXT_SSML,
    TextType='ssml',
)

# Write the audio stream to disk.
output_path = 'output.mp3'
with open(output_path, 'wb') as f:
    f.write(response['AudioStream'].read())

print(f"Saved synthesized speech → {output_path}")
