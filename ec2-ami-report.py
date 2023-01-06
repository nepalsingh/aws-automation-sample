import boto3
import json, logging

"""
aws ec2 describe-instances --query "Reservations[].Instances[].{amiID:ImageId,InstanceCreationDate:LaunchTime,Name:Tags[?Key=='Name']|[0].Value,InstaceId,Status:State.Name} --filter Name=instance-state-name, Values=running --output table

aws ec2 describe-images --image-ids <I'd goes here from previous command> --query "Images[*].{AWSAccount:OwnerId,DateofCreation:CreationDate,amiName:Name}" --output table

"""
def main():
  print(f'main function ...>1')
  ec2 = boto3.client('ec2')
  response = ec2.describe_instances()
  instance_data= []
  instance_dict = {}

  # print(f'response {response["Reservations"][0]["Instances"]}')
  for reservations in response["Reservations"]:
    for item in reservations["Instances"]:
      AMI_image_list = []
      # print(f'InstanceID: {item["InstanceId"]},  AMI-ID: {item["ImageId"]}, InstanceCreationDate: {item["LaunchTime"]}, Tags: {item["Tags"]}')
      instance_dict['InstanceId'] = item["InstanceId"]
      instance_dict['ImageId'] = item["ImageId"]
      instance_dict['InstanceCreationDate'] = item["LaunchTime"]
      for tag in item["Tags"]:
        print(f'tag: {tag} key = {tag.get("Key")} val={tag.get("Value")}')
        if tag.get('Key') == "Name":
            instance_name = tag.get('Value')
          # else:
          #     instance_name = None
      instance_dict['InstanceName'] = instance_name
      AMI_image_list.append(item["ImageId"])
      response_image = ec2.describe_images(ImageIds=AMI_image_list)
      for image in response_image['Images']:
        # print(f'image: {image}')
        try:
          # print(f'CreationDate: {image["CreationDate"]}, name: {image["Name"]}, owner: {image["OwnerId"]}')
          instance_dict['Image_CreationDate'] = image["CreationDate"]
          instance_dict['Image_Name'] = image["Name"]
          instance_dict['OwnerId'] = image["OwnerId"]
        except Exception as e:
          print(f'Err {str(e)}')
      instance_data.append(instance_dict)

  print(f'Result: {instance_data}')

if __name__=="__main__":
  main()