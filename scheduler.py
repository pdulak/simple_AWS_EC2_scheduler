import boto3
from datetime import datetime

#
# configuration
#
region_name='us-east-1'
instances_to_check = { 'tag_name': 'scheduler_name', 'tag_value': 'canada_office' }
start_times = [ '4:00', '14:00' ]
stop_times = [ '4:30', '16:00' ]
check_by_n_minutes = 15

#
# no changes required past this line
#

print('Scheduler started')
print('Current time is: {}'.format(datetime.now().strftime('%H:%M')) )

#
# Checking if the instances should be started or stopped
#
action_to_take = 'no action'
current_time = datetime.now().hour * 100 + datetime.now().minute

for start_time in start_times:
    num_time = int(start_time.replace(':',''))
    if (current_time >= num_time) & (current_time <= (num_time + check_by_n_minutes)):
        action_to_take = 'start'

for stop_time in stop_times:
    num_time = int(stop_time.replace(':',''))
    if (current_time >= num_time) & (current_time <= (num_time + check_by_n_minutes)):
        action_to_take = 'stop'

print('Action to take: {}'.format(action_to_take))

if action_to_take != 'no action':
    #
    # Looking for the instances to check
    #
    ec2 = boto3.resource('ec2', region_name=region_name)
    ec2_client = boto3.client('ec2', region_name=region_name)
    custom_filter = [
        {'Name':'tag:' + instances_to_check['tag_name'],
         'Values': [ instances_to_check['tag_value'] ] }
    ]
    instances = ec2.instances.filter(Filters=custom_filter)


    print('----- Instances to check: -----')
    for instance in instances:
        print('Checking {}...'.format(instance.id))

        if (instance.state['Name'] == 'running') & (action_to_take == 'stop'):
            print('Instance {} in the state "{}" should be stopped'.format(instance.id, instance.state['Name']))
            ec2_client.stop_instances(InstanceIds=[ instance.id ], DryRun=False)

        if (instance.state['Name'] == 'stopped') & (action_to_take == 'start'):
            print('Instance {} in the state "{}" should be started'.format(instance.id, instance.state['Name']))
            ec2_client.start_instances(InstanceIds=[ instance.id ], DryRun=False)

print('Scheduler finished')
