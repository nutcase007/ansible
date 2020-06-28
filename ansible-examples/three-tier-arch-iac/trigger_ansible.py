import json
import time
import boto3
import subprocess

SQS_QUEUE = 'https://sqs.us-east-1.amazonaws.com/285634635313/Notify-to-Ansible-Tower'
AWS_REGION = 'us-east-1'
DEFAULT_INVENTORY = 1

# set up our AWS endpoints
ec2_conn = boto3.client('ec2', region_name=AWS_REGION)
sqs_conn = boto3.client('sqs', region_name=AWS_REGION)

def get_instance(instance_id):
    response = ec2_conn.describe_instances(InstanceIds=[instance_id])
    # TODO catch error if instance does not exist
    print("response ", response)
    return response['Reservations'][0]['Instances'][0]

def remove_instance_from_inventory(msg):
    return

def run_command(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    print ("Command output : ", output)
    print ("Command exit status/return code : ", p_status)
    return p_status

def run_ansible_playbook(msg):
    instance_id = msg['detail']['instance-id']
    instance = get_instance(instance_id)
    print("instance ", instance)
    private_ip_address = instance['PrivateIpAddress']
    print("private_ip_address ", private_ip_address)
    cmd = "ansible-playbook /root/ansible/playbooks/site.yml -i /etc/ansible/ec2.py -l " + private_ip_address
    print(cmd)
    status = run_command(cmd)
    print ("status ", status)
    return status

def get_message():
    response = sqs_conn.receive_message(QueueUrl=SQS_QUEUE, MaxNumberOfMessages=1, MessageAttributeNames=['All'],VisibilityTimeout=0, WaitTimeSeconds=0)
    if 'Messages' in response:
        return response['Messages'][0]
    return None

def delete_message(m):
    sqs_conn.delete_message(QueueUrl=SQS_QUEUE, ReceiptHandle=m['ReceiptHandle'])

def main():
    while True:
        m = get_message()
        print("queue message ", m)
        if m:
            msg = json.loads(m['Body'])
            if 'detail' not in msg:
                return
            if 'state' not in msg['detail']:
                return
            try:
                if msg['detail']['state'] == "pending" or msg['detail']['state'] == "running":
                    status = run_ansible_playbook(msg)
                    if status == 0:
                        print ("status ", status)
                        delete_message(m)
                elif msg['detail']['state'] == "stopping":
                    remove_instance_from_inventory(msg)
                    delete_message(m)
                else:
                    delete_message(m)
            except Exception as e:
                # TODO handle more specific errors
                print(e)
        else:
            # no messages on queue
            print("pausing")
            time.sleep(60)

if __name__ == "__main__":
    main()