import { Construct } from 'constructs';
import * as k8s from './imports/k8s';


export interface PloneIngressOptions {
  readonly domain: string;
  readonly domainMaintenance?: string;
  readonly certIssuer?: string;
  readonly backendServiceName: string;
{% if cookiecutter.include_frontend == "yes" %}
  readonly frontendServiceName: string;
{% endif %}
}


export class PloneIngress extends Construct {
  constructor(scope: Construct, id: string, options: PloneIngressOptions) {
    super(scope, id);

    const annotations: { [key: string]: string } = {};
    if (options.certIssuer) {
      annotations['cert-manager.io/cluster-issuer'] = options.certIssuer;
    }

{% if cookiecutter.include_frontend == "yes" %}
    // Main ingress — frontend serves /, API requests go to backend
    new k8s.KubeIngress(this, 'main', {
      metadata: { annotations },
      spec: {
        tls: options.certIssuer ? [{
          hosts: [options.domain],
          secretName: `${options.domain}-tls`,
        }] : undefined,
        rules: [
          {
            host: options.domain,
            http: {
              paths: [
                {
                  path: '/++api++',
                  pathType: 'Prefix',
                  backend: {
                    service: {
                      name: options.backendServiceName,
                      port: { number: 8080 },
                    },
                  },
                },
                {
                  path: '/',
                  pathType: 'Prefix',
                  backend: {
                    service: {
                      name: options.frontendServiceName,
                      port: { number: 3000 },
                    },
                  },
                },
              ],
            },
          },
        ],
      },
    });
{% else %}
    // Main ingress — all traffic goes to backend (ClassicUI)
    new k8s.KubeIngress(this, 'main', {
      metadata: { annotations },
      spec: {
        tls: options.certIssuer ? [{
          hosts: [options.domain],
          secretName: `${options.domain}-tls`,
        }] : undefined,
        rules: [
          {
            host: options.domain,
            http: {
              paths: [
                {
                  path: '/',
                  pathType: 'Prefix',
                  backend: {
                    service: {
                      name: options.backendServiceName,
                      port: { number: 8080 },
                    },
                  },
                },
              ],
            },
          },
        ],
      },
    });
{% endif %}

    // Maintenance ingress — direct backend access
    if (options.domainMaintenance) {
      new k8s.KubeIngress(this, 'maintenance', {
        metadata: { annotations },
        spec: {
          tls: options.certIssuer ? [{
            hosts: [options.domainMaintenance],
            secretName: `${options.domainMaintenance}-tls`,
          }] : undefined,
          rules: [{
            host: options.domainMaintenance,
            http: {
              paths: [{
                path: '/',
                pathType: 'Prefix',
                backend: {
                  service: {
                    name: options.backendServiceName,
                    port: { number: 8080 },
                  },
                },
              }],
            },
          }],
        },
      });
    }
  }
}
