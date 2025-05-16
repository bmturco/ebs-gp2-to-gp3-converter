# EBS GP2 to GP3 Converter

A Python script that converts AWS EBS `gp2` volumes to `gp3` in the `us-east-1` region. 
Only converts volumes attached to **stopped EC2 instances**.

## Features

- Dry-run support
- Logs all activity to `ebs_conversion.log`
- Uses AWS Boto3 SDK

## Prerequisites

- Python 3.7+
- AWS CLI configured with credentials
- boto3 installed

## Installation

```bash
git clone https://github.com/yourusername/ebs-gp2-to-gp3-converter.git
cd ebs-gp2-to-gp3-converter
pip install -r requirements.txt
