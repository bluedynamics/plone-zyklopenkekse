import { Construct } from 'constructs';
import { Names } from 'cdk8s';
import * as cnpg from './imports/postgresql.cnpg.io';


export interface CloudNativePGClusterOptions {
  readonly instances?: number;
  readonly storageSize?: string;
}


export class CloudNativePGCluster extends Construct {
  public readonly serviceName: string;
  public readonly secretName: string;

  constructor(scope: Construct, id: string, options: CloudNativePGClusterOptions = {}) {
    super(scope, id);

    const cluster = new cnpg.Cluster(this, 'cluster', {
      spec: {
        instances: options.instances ?? 2,
        postgresql: {
          parameters: {
            shared_buffers: '256MB',
          },
        },
        bootstrap: {
          initdb: {
            database: 'plone',
            owner: 'plone',
          },
        },
        storage: {
          size: options.storageSize ?? '20Gi',
        },
      },
    });

    const clusterName = Names.toLabelValue(cluster);
    this.serviceName = `${clusterName}-rw`;
    this.secretName = `${clusterName}-app`;
  }
}
