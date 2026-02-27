import { Construct } from 'constructs';
import { App, Chart, ChartProps } from 'cdk8s';
import { Plone{% if cookiecutter.include_varnish == "yes" %}, PloneHttpcache{% endif %} } from '@bluedynamics/cdk8s-plone';
import * as kplus from 'cdk8s-plus-30';
{% if cookiecutter.include_cnpg == "yes" %}
import { CloudNativePGCluster } from './postgres';
{% endif %}
{% if cookiecutter.include_ingress == "yes" %}
import { PloneIngress } from './ingress';
{% endif %}
import * as process from 'process';


export class {{ cookiecutter.project_name | capitalize }}Chart extends Chart {
  constructor(scope: Construct, id: string, props: ChartProps = {}) {
    super(scope, id, props);

    const image = process.env.IMAGE ?? '{{ cookiecutter.__container_registry }}/{{ cookiecutter.__target }}:latest';
{% if cookiecutter.include_cnpg == "yes" %}

    // ---- PostgreSQL (CloudNativePG) ----
    const db = new CloudNativePGCluster(this, 'db', {
      instances: Number(process.env.PG_INSTANCES ?? '2'),
      storageSize: process.env.PG_STORAGE ?? '20Gi',
    });

    const env = new kplus.Env([], {
      SECRET_POSTGRESQL_USERNAME: {
        valueFrom: { secretKeyRef: { name: `${db.secretName}`, key: 'username' } },
      },
      SECRET_POSTGRESQL_PASSWORD: {
        valueFrom: { secretKeyRef: { name: `${db.secretName}`, key: 'password' } },
      },
      INSTANCE_db_storage: { value: 'relstorage' },
      INSTANCE_db_blob_mode: { value: 'cache' },
      INSTANCE_db_relstorage: { value: 'postgresql' },
      INSTANCE_db_relstorage_postgresql_dsn: {
        value: `host='${db.serviceName}' dbname='plone' user='$(SECRET_POSTGRESQL_USERNAME)' password='$(SECRET_POSTGRESQL_PASSWORD)'`,
      },
    });
{% else %}

    // ---- Database environment (configure for your database) ----
    const env = new kplus.Env([], {
      INSTANCE_db_storage: { value: 'relstorage' },
      INSTANCE_db_blob_mode: { value: 'cache' },
      INSTANCE_db_relstorage: { value: 'postgresql' },
      INSTANCE_db_relstorage_postgresql_dsn: {
        value: "host='db-host' dbname='plone' user='plone' password='secret'",
      },
    });
{% endif %}

    // ---- Plone (unified image, args select role) ----
    const plone = new Plone(this, 'plone', {
      version: process.env.IMAGE_TAG ?? 'latest',
      backend: {
        image: image,
        args: ['start-backend'],
        environment: env,
        replicas: Number(process.env.BACKEND_REPLICAS ?? '2'),
      },
      frontend: {
        image: image,
        args: ['start-frontend'],
        replicas: Number(process.env.FRONTEND_REPLICAS ?? '2'),
      },
    });
{% if cookiecutter.include_varnish == "yes" %}

    // ---- Varnish HTTP cache ----
    const httpcache = new PloneHttpcache(this, 'httpcache', {
      plone: plone,
    });
{% endif %}
{% if cookiecutter.include_ingress == "yes" %}

    // ---- Ingress ----
    new PloneIngress(this, 'ingress', {
      domain: process.env.DOMAIN ?? '{{ cookiecutter.project_name }}.example.com',
      domainMaintenance: process.env.DOMAIN_MAINTENANCE ?? 'admin.{{ cookiecutter.project_name }}.example.com',
      certIssuer: process.env.CERT_ISSUER ?? 'letsencrypt-prod',
      backendServiceName: plone.backendServiceName,
      frontendServiceName: plone.frontendServiceName ?? '',
    });
{% endif %}
  }
}

const app = new App();
new {{ cookiecutter.project_name | capitalize }}Chart(app, '{{ cookiecutter.__target }}');
app.synth();
