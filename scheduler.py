import boto3
from datetime import datetime

#
# configuration
#

#
# region_name - the region that should be covered by the scheduler
#
region_name='us-east-1'
#
# instances_to_check - instances are found by the tag name and tag value. In the example
# below, the tag name is "scheduler_name" and the tag value is "canada_office"
#
instances_to_check = { 'tag_name': 'scheduler_name', 'tag_value': 'canada_office' }
#
# start_times - the list of the start times during the day, using 24h notation, for 
# example, if the instances should be started at 8:00 only, set this value to [ '8:00' ]
# if they should be started at 4:00 and 14:00, set to [ '4:00', '14:00' ]
#
# stop_times - the list of the stop times, defined in the same way as start_times
#
start_times = [ '4:00', '14:00' ]
stop_times = [ '4:30', '16:00' ]
#
# check_by_n_minutes - the number of minutes after start or stop time during which
# the scheduler will check if the instance is running.
#
check_by_n_minutes = 15

#########################################################################################
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
