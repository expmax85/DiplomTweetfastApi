FROM fluent/fluentd:v1.15-debian-1
USER root
RUN ["gem", "install", "elasticsearch", "--no-document", "--version", "8.0.0"]
RUN ["gem", "install", "fluent-plugin-elasticsearch", "--no-document", "--version", "5.2.4"]
RUN ["gem", "install", "fluent-plugin-grok-parser", "--no-document"]
USER fluent