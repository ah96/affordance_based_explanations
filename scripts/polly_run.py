import boto3

# Initialize Polly client
polly_client = boto3.client('polly', region_name='us-west-2')

# Synthesize speech with pitch adjustment
response = polly_client.synthesize_speech(
    VoiceId='Joanna',
    OutputFormat='mp3',
    Text='<speak><prosody pitch="+20%">Hello, this is a test with a higher pitch.</prosody></speak>',
    TextType='ssml'
)

# Save the response audio to a file
with open('output.mp3', 'wb') as file:
    file.write(response['AudioStream'].read())
