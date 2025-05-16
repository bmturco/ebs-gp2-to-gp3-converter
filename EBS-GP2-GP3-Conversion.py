import boto3
import logging
from botocore.exceptions import ClientError

# Configuration
REGION = 'us-east-1'
LOG_FILE = 'ebs_conversion.log'
DRY_RUN = True  # Set to False to actually perform the modification

# Set up logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

ec2 = boto3.client('ec2', region_name=REGION)

def get_instance_state(instance_id):
    try:
        response = ec2.describe_instances(InstanceIds=[instance_id])
        state = response['Reservations'][0]['Instances'][0]['State']['Name']
        return state
    except Exception as e:
        logging.error("Failed to get state for instance %s: %s", instance_id, str(e))
        return None

def convert_gp2_volumes_on_stopped_instances():
    try:
        volumes = ec2.describe_volumes(
            Filters=[{'Name': 'volume-type', 'Values': ['gp2']}]
        )['Volumes']

        if not volumes:
            logging.info("No gp2 volumes found in region %s", REGION)
            return

        for vol in volumes:
            vol_id = vol['VolumeId']
            attachments = vol.get('Attachments', [])

            if not attachments:
                logging.info("Volume %s is not attached to any instance. Skipping.", vol_id)
                continue

            instance_id = attachments[0]['InstanceId']
            state = get_instance_state(instance_id)

            if state != 'stopped':
                logging.info("Instance %s (attached to volume %s) is not stopped (%s). Skipping.",
                             instance_id, vol_id, state)
                continue

            logging.info("Attempting to convert volume %s to gp3 (attached to stopped instance %s, dry-run=%s)",
                         vol_id, instance_id, DRY_RUN)

            try:
                ec2.modify_volume(
                    VolumeId=vol_id,
                    VolumeType='gp3',
                    DryRun=DRY_RUN
                )
                msg = f"{'[DRY-RUN]' if DRY_RUN else '[MODIFIED]'} Volume {vol_id} (instance {instance_id}) converted to gp3"
                print(msg)
                logging.info(msg)

            except ClientError as e:
                if 'DryRunOperation' in str(e):
                    print(f"[DRY-RUN] Dry-run succeeded for volume {vol_id}")
                    logging.info("Dry-run successful for volume %s", vol_id)
                else:
                    print(f"[ERROR] Failed to convert volume {vol_id}: {e}")
                    logging.error("Failed to convert volume %s: %s", vol_id, str(e))

    except ClientError as e:
        logging.error("Failed to describe volumes: %s", str(e))

if __name__ == "__main__":
    convert_gp2_volumes_on_stopped_instances()
