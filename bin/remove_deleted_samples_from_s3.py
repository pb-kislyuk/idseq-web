#!/usr/bin/env python
import os
import boto3

ENV = 'staging' # change to prod as necessary
DB_SAMPLES_FILENAME = '/tmp/{env}_db_sample_ids'.format(env=ENV)
S3_SAMPLES_FILENAME = '/tmp/{env}_s3_sample_paths'.format(env=ENV)

def fetch_sample_ids():
  print('Fetching ids from idseq_{env}.samples table'.format(env=ENV))
  os.system('bin/clam {env} \'echo "select id from samples;" > samples.sql; mysql -h $RDS_ADDRESS -u $DB_USERNAME --password=$DB_PASSWORD idseq_{env} < samples.sql; rm samples.sql\' > {outfile}'.format(outfile=DB_SAMPLES_FILENAME, env=ENV))

def fetch_s3_paths():
  print('Fetching sample paths under s3://idseq-samples-{env}'.format(env=ENV))
  os.system('for dir in `aws s3 ls s3://idseq-samples-{env}/samples/ | awk \'{{print $2}}\'`; do aws s3 ls s3://idseq-samples-{env}/samples/$dir | awk -v dir=$dir \'{{print dir $2}}\'; done > {outfile}'.format(outfile = S3_SAMPLES_FILENAME, env=ENV))
  
def db_sample_dict():
  return_dict = {}
  db_samples_file = open(DB_SAMPLES_FILENAME, 'r')
  line = db_samples_file.readline() # first line says 'id'
  while True:
    line = db_samples_file.readline().strip()
    if not line:
      break
    return_dict[line] = 1
  return return_dict

def delete_unknown_samples(dryrun):
  s3 = boto3.resource('s3')
  pd = db_sample_dict()
  bucket='idseq-samples-{env}'.format(env=ENV)
  s3_samples_file = open(S3_SAMPLES_FILENAME, 'r')
  while True:
    line = s3_samples_file.readline()
    if not line:
      break
    sample_id = line.split('/')[1]
    if sample_id not in pd:
      subpath = line.strip()
      print('{verb}: idseq-samples-{env}/samples/{subpath}'.format(
        verb = 'Found' if dryrun else 'Deleting', env=ENV, subpath=subpath))
      if not dryrun:
        while True:
          resp = s3.meta.client.list_object_versions(
              Bucket=bucket,
              Prefix='samples/{subpath}'.format(subpath=subpath))
          objects_to_delete = resp.get('Versions', [])
          if len(objects_to_delete) == 0:
            break

          delete_keys = {'Objects' : []}
          count = 0
          for item in objects_to_delete:
            delete_keys['Objects'].append({'Key': item['Key'], 'VersionId': item['VersionId']})
            count += 1
            if count == 1000: #s3 API only returns and accepts up to 1000 objects at a time
              break

          print(' Deleting {count} objects'.format(count=count))
          s3.meta.client.delete_objects(Bucket=bucket, Delete=delete_keys)
          if count < 1000: #if we deleted fewer than 1000 objects then no need to check the path again
            break

if __name__ == "__main__":
  msg = 'This utility will delete all s3 sample data without db entries in the {env} environment. Type "y" or "yes" to continue.\n'.format(env=ENV)
  resp = input(msg)
  if resp.lower() not in ["y", "yes"]:
    print("Exiting...")
    quit()
  fetch_s3_paths()
  fetch_sample_ids()
  delete_unknown_samples(dryrun=True)
  input('Press enter to continue')
  delete_unknown_samples(dryrun=False)
