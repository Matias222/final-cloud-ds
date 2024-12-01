import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as glue from 'aws-cdk-lib/aws-glue';

export class ProyectoFinalStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vpc = new ec2.Vpc(this, 'PublicVpc', {
      maxAzs: 1,
      subnetConfiguration: [
        {
          name: 'PublicSubnet',
          subnetType: ec2.SubnetType.PUBLIC,
        },
      ],
      natGateways: 0,
    });

    const securityGroup = new ec2.SecurityGroup(this, 'OpenSecurityGroup', {
      vpc,
      description: 'Allow all traffic from anywhere',
      allowAllOutbound: true,
    });

    securityGroup.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.allTraffic(), 'Allow all inbound traffic');

    const ubuntuAmi = ec2.MachineImage.genericLinux({
      'us-east-2': 'ami-048f97d041d14fd4e',
    });

    const environments = ['dev', 'test', 'prod'];

    environments.forEach(env => {

      const userData = ec2.UserData.forLinux();
      userData.addCommands(
        'sudo apt update -y',
        'sudo apt install -y docker.io',
        'sudo apt install -y git',
        'sudo apt install -y docker-compose',
        'sudo systemctl enable docker',
        'sudo systemctl start docker',
        'sudo git clone https://github.com/Matias222/final-cloud-ds.git'
      );

      new ec2.Instance(this, `${env}-Instance`, {
        vpc,
        instanceType: ec2.InstanceType.of(ec2.InstanceClass.T2, ec2.InstanceSize.MICRO), 
        machineImage: ubuntuAmi,
        securityGroup,
        keyName: 'utec_proyecto',
        userData,
      });

      new glue.CfnDatabase(this, `${env}-GlueDatabase`, {
        catalogId: this.account,
        databaseInput: {
          name: `proyectofinal-${env}-database`,
          description: `Glue database for the ${env} environment`,
        },
      });
    
      new s3.Bucket(this, `${env}-Bucket`, {
        bucketName: `proyectofinal-${env}-bucket-${this.account}`,
        versioned: true,
        removalPolicy: cdk.RemovalPolicy.DESTROY,
        autoDeleteObjects: true,
      });
    
    });

  }
}
