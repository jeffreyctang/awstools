#!/usr/bin/python
import boto.ec2
import json
import time


instance_id='i-9dac413e'
snap_id='snap-fce21e88'

conn=boto.ec2.connect_to_region('us-east-1')

instance=conn.get_only_instances(instance_ids=[instance_id])[0]
#print instance.block_device_mapping
#print instance.root_device_name

# shutdown instance
stopped=conn.stop_instances([instance_id])
print stopped


# create newvolume from snapshot
snapshot=conn.get_all_snapshots(snapshot_ids=[snap_id])[0]
print snapshot
new_volume=snapshot.create_volume('us-east-1c', volume_type='gp2')
new_volume_id=new_volume.id

print new_volume_id
while True:
    time.sleep(1)
    print "waiting for volume to become available"
    if conn.get_all_volumes([new_volume_id])[0].status == 'available':
        break

# force detach volume from instance

while '/dev/sda1' in instance.block_device_mapping:
    old_volume=instance.block_device_mapping['/dev/sda1']
    print "waiting for detach of: %s" % old_volume
    try:
        conn.detach_volume(old_volume.volume_id,instance_id,force=True)
    except:
        pass
    time.sleep(1)
    instance=conn.get_only_instances(instance_ids=[instance_id])[0]


# attach newvolume to instance
conn.attach_volume(new_volume_id,instance_id,'/dev/sda1')
conn.delete_volume(old_volume.volume_id)
   

conn.start_instances([instance_id])


# start instance

# remove oldvolume

