# dpps

![Version: 0.0.0-dev](https://img.shields.io/badge/Version-0.0.0--dev-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 0.0.0-dev](https://img.shields.io/badge/AppVersion-0.0.0--dev-informational?style=flat-square)

A Helm chart for the DPPS project

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| The DPPS Authors |  |  |

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| https://fluent.github.io/helm-charts | fluent-bit | 0.48.9 |
| https://grafana.github.io/helm-charts | grafana | 9.2.2 |
| https://grafana.github.io/helm-charts | loki | 6.30.1 |
| https://prometheus-community.github.io/helm-charts | prometheus | 27.20.0 |
| oci://harbor.cta-observatory.org/dpps | bdms | v0.3.1 |
| oci://harbor.cta-observatory.org/dpps | cert-generator-grid | v2.1.0 |
| oci://harbor.cta-observatory.org/dpps | wms | v0.3.1 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| bdms.cert-generator-grid.enabled | bool | `true` |  |
| bdms.configure_test_setup | bool | `true` |  |
| bdms.database.default | string | `"postgresql://rucio:XcL0xT9FgFgJEc4i3OcQf2DMVKpjIWDGezqcIPmXlM@dpps-postgresql:5432/rucio"` |  |
| bdms.enabled | bool | `true` | Whether to deploy BDMS |
| bdms.postgresql.global.postgresql.auth.database | string | `"rucio"` |  |
| bdms.postgresql.global.postgresql.auth.password | string | `"XcL0xT9FgFgJEc4i3OcQf2DMVKpjIWDGezqcIPmXlM"` |  |
| bdms.postgresql.global.postgresql.auth.username | string | `"rucio"` |  |
| bdms.rucio-daemons.config.database.default | string | `"postgresql://rucio:XcL0xT9FgFgJEc4i3OcQf2DMVKpjIWDGezqcIPmXlM@dpps-postgresql:5432/rucio"` |  |
| bdms.rucio-daemons.conveyorTransferSubmitterCount | int | `1` |  |
| bdms.rucio-server.authRucioHost | string | `"rucio-server.local"` |  |
| bdms.rucio-server.config.database.default | string | `"postgresql://rucio:XcL0xT9FgFgJEc4i3OcQf2DMVKpjIWDGezqcIPmXlM@dpps-postgresql:5432/rucio"` |  |
| bdms.rucio-server.exposeErrorLogs | bool | `false` |  |
| bdms.rucio-server.ftsRenewal.enabled | bool | `false` |  |
| bdms.rucio-server.httpd_config.grid_site_enabled | string | `"True"` |  |
| bdms.rucio-server.ingress.enabled | bool | `true` |  |
| bdms.rucio-server.ingress.hosts[0] | string | `"rucio-server.local"` |  |
| bdms.rucio-server.livenessProbe.initialDelaySeconds | int | `40` |  |
| bdms.rucio-server.livenessProbe.periodSeconds | int | `10` |  |
| bdms.rucio-server.livenessProbe.successThreshold | int | `1` |  |
| bdms.rucio-server.livenessProbe.timeoutSeconds | int | `15` |  |
| bdms.rucio-server.optional_config.RUCIO_CFG_BOOTSTRAP_USERPASS_IDENTITY | string | `"dpps"` |  |
| bdms.rucio-server.optional_config.RUCIO_CFG_BOOTSTRAP_USERPASS_PWD | string | `"secret"` |  |
| bdms.rucio-server.optional_config.RUCIO_CFG_BOOTSTRAP_X509_EMAIL | string | `"dpps-test@cta-observatory.org"` |  |
| bdms.rucio-server.optional_config.RUCIO_CFG_BOOTSTRAP_X509_IDENTITY | string | `"CN=DPPS User"` |  |
| bdms.rucio-server.optional_config.RUCIO_CFG_COMMON_EXTRACT_SCOPE | string | `"ctao_bdms"` |  |
| bdms.rucio-server.optional_config.RUCIO_CFG_POLICY_LFN2PFN_ALGORITHM_DEFAULT | string | `"ctao_bdms"` |  |
| bdms.rucio-server.optional_config.RUCIO_CFG_POLICY_PACKAGE | string | `"bdms_rucio_policy"` |  |
| bdms.rucio-server.readinessProbe.initialDelaySeconds | int | `40` |  |
| bdms.rucio-server.readinessProbe.periodSeconds | int | `10` |  |
| bdms.rucio-server.readinessProbe.successThreshold | int | `1` |  |
| bdms.rucio-server.readinessProbe.timeoutSeconds | int | `15` |  |
| bdms.rucio-server.replicaCount | int | `1` |  |
| bdms.rucio-server.service.name | string | `"https"` |  |
| bdms.rucio-server.service.port | int | `443` |  |
| bdms.rucio-server.service.protocol | string | `"TCP"` |  |
| bdms.rucio-server.service.targetPort | int | `443` |  |
| bdms.rucio-server.service.type | string | `"ClusterIP"` |  |
| bdms.rucio-server.useSSL | bool | `true` |  |
| bdms.safe_to_bootstrap_rucio | bool | `true` |  |
| cert-generator-grid.enabled | bool | `false` |  |
| cert-generator-grid.generatePreHooks | bool | `true` |  |
| dev.client_image_tag | string | `nil` | tag of the image used to run helm tests |
| dev.mount_repo | bool | `true` | mount the repo volume to test the code as it is being developed |
| dev.n_test_jobs | int | `1` | number of parallel test jobs for pytest |
| dev.pipelines | object | `{"calibpipe":{"version":"v0.2.0"},"datapipe":{"version":"v0.2.1"}}` | Pipelines versions used in the tests |
| dev.runAsGroup | int | `1000` |  |
| dev.runAsUser | int | `1000` | user to run the container as. needs to be the same as local user if writing to repo directory |
| dev.run_tests | bool | `true` | run tests in the container |
| dev.sleep | bool | `false` | sleep after test to allow interactive development |
| dev.start_long_running_client | bool | `false` | if true, a long-running client container will start *instead* of a test container |
| fluent-bit.config.inputs | string | `"[INPUT]\n    Name tail\n    Path /var/log/containers/*.log\n    multiline.parser docker, cri\n    Tag kube.*\n    Mem_Buf_Limit 5MB\n    Buffer_Chunk_Size 1\n    Refresh_Interval 1\n    Skip_Long_Lines On\n"` |  |
| fluent-bit.config.outputs | string | `"[FILTER]\n    Name grep\n    Match *\n\n[OUTPUT]\n    Name        loki\n    Match       *\n    Host        dpps-loki-gateway\n    port        80\n    tls         off\n    tls.verify  off\n"` |  |
| fluent-bit.config.rbac.create | bool | `true` |  |
| fluent-bit.config.rbac.eventsAccess | bool | `true` |  |
| fluent-bit.enabled | bool | `true` |  |
| global.image.registry | string | `"harbor.cta-observatory.org/proxy_cache"` |  |
| grafana.adminPassword | string | `"admin"` |  |
| grafana.adminUser | string | `"admin"` |  |
| grafana.dashboardProviders."dashboardproviders.yaml".apiVersion | int | `1` |  |
| grafana.dashboardProviders."dashboardproviders.yaml".providers[0].editable | bool | `true` |  |
| grafana.dashboardProviders."dashboardproviders.yaml".providers[0].name | string | `"default"` |  |
| grafana.dashboardProviders."dashboardproviders.yaml".providers[0].options.path | string | `"/var/lib/grafana/dashboards/default"` |  |
| grafana.dashboardProviders."dashboardproviders.yaml".providers[0].type | string | `"file"` |  |
| grafana.dashboardProviders."dashboardproviders.yaml".providers[1].editable | bool | `true` |  |
| grafana.dashboardProviders."dashboardproviders.yaml".providers[1].name | string | `"sidecar"` |  |
| grafana.dashboardProviders."dashboardproviders.yaml".providers[1].options.path | string | `"/var/lib/grafana/dashboards/sidecar"` |  |
| grafana.dashboardProviders."dashboardproviders.yaml".providers[1].type | string | `"file"` |  |
| grafana.dashboards.default.k8-views-global.datasource | string | `"Prometheus"` |  |
| grafana.dashboards.default.k8-views-global.gnetId | int | `15757` |  |
| grafana.dashboards.default.k8-views-global.revision | int | `43` |  |
| grafana.dashboards.default.k8-views-namespaces.datasource | string | `"Prometheus"` |  |
| grafana.dashboards.default.k8-views-namespaces.gnetId | int | `15758` |  |
| grafana.dashboards.default.k8-views-namespaces.revision | int | `42` |  |
| grafana.dashboards.default.k8-views-nodes.datasource | string | `"Prometheus"` |  |
| grafana.dashboards.default.k8-views-nodes.gnetId | int | `15759` |  |
| grafana.dashboards.default.k8-views-nodes.revision | int | `37` |  |
| grafana.dashboards.default.k8-views-pods.datasource | string | `"Prometheus"` |  |
| grafana.dashboards.default.k8-views-pods.gnetId | int | `15760` |  |
| grafana.dashboards.default.k8-views-pods.revision | int | `36` |  |
| grafana.datasources."datasources.yaml".apiVersion | int | `1` |  |
| grafana.datasources."datasources.yaml".datasources[0].access | string | `"proxy"` |  |
| grafana.datasources."datasources.yaml".datasources[0].name | string | `"Prometheus"` |  |
| grafana.datasources."datasources.yaml".datasources[0].type | string | `"prometheus"` |  |
| grafana.datasources."datasources.yaml".datasources[0].url | string | `"http://dpps-prometheus-server"` |  |
| grafana.datasources."datasources.yaml".datasources[1].access | string | `"proxy"` |  |
| grafana.datasources."datasources.yaml".datasources[1].jsonData.maxLines | int | `1000` |  |
| grafana.datasources."datasources.yaml".datasources[1].jsonData.timeout | int | `60` |  |
| grafana.datasources."datasources.yaml".datasources[1].name | string | `"Loki"` |  |
| grafana.datasources."datasources.yaml".datasources[1].type | string | `"loki"` |  |
| grafana.datasources."datasources.yaml".datasources[1].url | string | `"http://dpps-loki:3100"` |  |
| grafana.enabled | bool | `true` |  |
| grafana.image.registry | string | `"harbor.cta-observatory.org/proxy_cache"` |  |
| grafana.ingress.enabled | bool | `true` |  |
| grafana.ingress.hosts[0] | string | `"grafana.dpps.local"` |  |
| grafana.persistentVolume.size | string | `"100Mi"` |  |
| grafana.prometheus-node-exporter.enabled | bool | `false` |  |
| grafana.retention | string | `"1d"` |  |
| grafana.sidecar.dashboards.defaultFolderName | string | `"Sidecar Dashboards"` |  |
| grafana.sidecar.dashboards.enabled | bool | `true` |  |
| grafana.sidecar.dashboards.folder | string | `"/var/lib/grafana/dashboards/sidecar"` |  |
| grafana.sidecar.dashboards.folderAnnotation | string | `"grafana_folder"` |  |
| grafana.sidecar.dashboards.provider.name | string | `"sidecar"` |  |
| grafana.sidecar.dashboards.searchNamespace | string | `"ALL"` |  |
| grafana.sidecar.image.registry | string | `"harbor.cta-observatory.org/proxy_cache"` |  |
| grafana.testFramework.enabled | bool | `false` |  |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository_prefix | string | `"harbor.cta-observatory.org/dpps/dpps"` |  |
| loki.backend.replicas | int | `0` |  |
| loki.bloomCompactor.replicas | int | `0` |  |
| loki.bloomGateway.replicas | int | `0` |  |
| loki.compactor.replicas | int | `0` |  |
| loki.deploymentMode | string | `"SingleBinary"` |  |
| loki.distributor.replicas | int | `0` |  |
| loki.enabled | bool | `true` |  |
| loki.indexGateway.replicas | int | `0` |  |
| loki.ingester.replicas | int | `0` |  |
| loki.loki.auth_enabled | bool | `false` |  |
| loki.loki.commonConfig.replication_factor | int | `1` |  |
| loki.loki.limits_config.allow_structured_metadata | bool | `true` |  |
| loki.loki.limits_config.volume_enabled | bool | `true` |  |
| loki.loki.pattern_ingester.enabled | bool | `true` |  |
| loki.loki.ruler.enable_api | bool | `true` |  |
| loki.loki.schemaConfig.configs[0].from | string | `"2024-04-01"` |  |
| loki.loki.schemaConfig.configs[0].index.period | string | `"24h"` |  |
| loki.loki.schemaConfig.configs[0].index.prefix | string | `"loki_index_"` |  |
| loki.loki.schemaConfig.configs[0].object_store | string | `"s3"` |  |
| loki.loki.schemaConfig.configs[0].schema | string | `"v13"` |  |
| loki.loki.schemaConfig.configs[0].store | string | `"tsdb"` |  |
| loki.memcached.image.repository | string | `"harbor.cta-observatory.org/proxy_cache/memcached"` |  |
| loki.memcached.image.tag | string | `"1.6.38-alpine3.22"` |  |
| loki.minio.enabled | bool | `true` |  |
| loki.minio.image.repository | string | `"harbor.cta-observatory.org/proxy_cache/minio/minio"` |  |
| loki.monitoring.selfMonitoring.enabled | bool | `false` |  |
| loki.monitoring.selfMonitoring.grafanaAgent.installOperator | bool | `false` |  |
| loki.monitoring.selfMonitoring.lokiCanary.enabled | bool | `false` |  |
| loki.querier.replicas | int | `0` |  |
| loki.queryFrontend.replicas | int | `0` |  |
| loki.queryScheduler.replicas | int | `0` |  |
| loki.read.replicas | int | `0` |  |
| loki.rollout_operator.enabled | bool | `false` |  |
| loki.singleBinary.replicas | int | `1` |  |
| loki.test.enabled | bool | `false` |  |
| loki.write.replicas | int | `0` |  |
| prometheus.alertmanager.enabled | bool | `false` |  |
| prometheus.enabled | bool | `true` |  |
| prometheus.prometheus-node-exporter.image.registry | string | `"harbor.cta-observatory.org/proxy_cache"` |  |
| prometheus.prometheus-node-exporter.image.repository | string | `"prom/node-exporter"` |  |
| prometheus.prometheus-pushgateway.enabled | bool | `false` |  |
| prometheus.server.image.repository | string | `"harbor.cta-observatory.org/proxy_cache/prom/prometheus"` |  |
| wms.cert-generator-grid.enabled | bool | `false` |  |
| wms.cvmfs.enabled | bool | `true` |  |
| wms.cvmfs.publish_docker_images[0] | string | `"harbor.cta-observatory.org/dpps/datapipe:v0.2.1"` |  |
| wms.cvmfs.publish_docker_images[1] | string | `"harbor.cta-observatory.org/dpps/calibpipe:v0.2.0"` |  |
| wms.enabled | bool | `true` | Whether to deploy WMS |
| wms.rucio.enabled | bool | `true` |  |
| wms.rucio.rucioConfig | string | `"dpps-bdms-rucio-config"` |  |

