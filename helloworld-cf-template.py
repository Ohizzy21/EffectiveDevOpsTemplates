"""Generating CloudFormation template."""

from troposphere import (
        Base64,
        ec2,
        GetAtt,
        Join,
        Output,
        Parameter,
        Ref,
        Template,
)

ApplicationPort = "3000"
t = Template()
t.add_description("Effective DevOps in AWS: HelloWorld web application")

t.add_parameter(Parameter(
    "KeyPair",
    Description="Name of an existing EC2 KeyPair to SSH",
    Type="AWS::EC2::KeyPair::KeyName",
    ConstraintDescription="must be the name of an existing EC2 KeyPair.",
))

t.add_resource(ec2.SecurityGroup(
        "SecurityGroup",
        GroupDescription="Allow SSH and TCP/{} access".format(ApplicationPort),
        SecurityGroupIngress=[
            ec2.SecurityGroupRule(
                IpProtocol="tcp",
                FromPort="22",
                ToPort="22",
                CidrIp="0.0.0.0/0",
            ),
            ec2.SecurityGroupRule(
                IpProtocol="tcp",
                FromPort=ApplicationPort,
                ToPort=ApplicationPort,
                CidrIp="0.0.0.0/0",
            ),
        ],
))

ud = Base64(Join('\n', [
    "#!/bin/bash",
    "sudo apt update",
    "sudo apt install nodejs",
    "wget http://bit.ly/2vESNuc -O /home/ubuntu/helloworld.js",
    "sudo wget https://raw.githubusercontent.com/Ohizzy21/EffectiveDevOpsTemplates/master/Helloworld.service -O /etc/systemd/system/helloworld.service",
    "sudo systemctl daemon-reload",
    "sudo systemctl enable helloworld",
    "sudo systemctl start helloworld"
#    "cat helloworld.js",
#    "wget http://bit.ly/2vVvT18 -O /home/ubuntu/helloworld.conf",
#    "sudo systemctl start helloworld"
]))

t.add_resource(ec2.Instance(
    "instance",
    ImageId="ami-085925f297f89fce1",
    InstanceType="t2.micro",
    SecurityGroups=[Ref("SecurityGroup")],
    KeyName=Ref("KeyPair"),
    UserData=ud,
))

t.add_output(Output(
    "InstancePublicIp",
    Description="Public IP of our instance.",
    Value=GetAtt("instance", "PublicIp"),
))

t.add_output(Output(
    "WebUrl",
    Description="Application endpoint",
    Value=Join("", [
        "http://", GetAtt("instance", "PublicDnsName"),
        ":", ApplicationPort
    ]),
))

print t.to_json()


