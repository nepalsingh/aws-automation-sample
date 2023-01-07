import boto3
import csv
import json
from datetime import datetime



"""
aws ec2 describe-instances --query "Reservations[].Instances[].{amiID:ImageId,InstanceCreationDate:LaunchTime,Name:Tags[?Key=='Name']|[0].Value,InstaceId,Status:State.Name} --filter Name=instance-state-name, Values=running --output table

aws ec2 describe-images --image-ids <I'd goes here from previous command> --query "Images[*].{AWSAccount:OwnerId,DateofCreation:CreationDate,amiName:Name}" --output table

"""

# csv file name
output_csv = "export.csv"

def CSV_Writer(content, header):
    with open(output_csv, "w") as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=header)
        writer.writeheader()
        for row in content:
            writer.writerow(row)


def main():
    Header = "Main Start"
    print(f'{Header:-^60}')
    ec2 = boto3.client("ec2")
    response = ec2.describe_instances()
    Instances = []
    instance_dict = {}
    AMI_image_list = []
    format_date = "%m-%d-%y %H:%M:%S.%f"

    # print(f'response {response["Reservations"][0]["Instances"]}')
    for reservations in response["Reservations"]:
        for item in reservations["Instances"]:
            if item["State"]["Name"] == "running":
                # print(f'InstanceID: {item["InstanceId"]},  AMI-ID: {item["ImageId"]}, InstanceCreationDate: {item["LaunchTime"]} ')
                instance_dict["InstanceId"] = item["InstanceId"]
                instance_dict["amiID"] = item["ImageId"]
                instance_dict["InstanceCreationDate"] = datetime.strftime(
                    item["LaunchTime"], format_date
                )
                instance_dict["Status"] = item["State"]["Name"]
                for tag in item["Tags"]:
                    if tag.get("Key") == "Name":
                        instance_name = tag.get("Value")
                    instance_dict["InstanceName"] = instance_name
                Instances.append(json.dumps(instance_dict))
                # print(f'json.dumps(instance_dict) {type(json.dumps(instance_dict))} {type(instance_dict)}')
            AMI_image_list.append(item["ImageId"])
            # print(f'AMI_image_list {AMI_image_list} instance_dict: {instance_dict} -- imageID: {item["ImageId"]}')
    # print(f'set(AMI_image_list) {[*set(AMI_image_list)]} -- {Instances}')
    response_image = ec2.describe_images(ImageIds=[*set(AMI_image_list)])
    ami_images = []
    for image in response_image["Images"]:
        image_dict = {}
        try:
            image_dict = { "amiID": image['ImageId'],
                "Image_CreationDate": image["CreationDate"],
                "Image_Name": image["Name"],
                "OwnerId": image["OwnerId"],
            }
            ami_images.append(json.dumps(image_dict))
        except Exception as e:
            print(f"Err {str(e)}")
    final_data = []
    for i in Instances:
        v = json.loads(i)
        for ami in ami_images:
          a = json.loads(ami)
          if a['amiID'] == v['amiID']:
            v.update(a)
          final_data.append(v)

    print(f'Output is Stored in : {output_csv}, instance Count: {len(Instances)}, Image Count {len(ami_images)} ')
    print(f'{"End":-^60}')
    header = [
        "InstanceId",
        "amiID",
        "InstanceCreationDate",
        "Status",
        "InstanceName",
        "Image_CreationDate",
        "Image_Name",
        "OwnerId",
    ]
    CSV_Writer(content=final_data, header=header)


if __name__ == "__main__":
    main()
