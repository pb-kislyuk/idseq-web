# Flag to turn elasticsearch callbacks on or off for Project/Sample/Metadatum/User models
ELASTICSEARCH_ON = (Rails.env != 'test')

# Initialize elasticsearch client
case Rails.env
when "production", "staging", "sandbox"
  port = '443'
when "development"
  port = '9200'
end

config = {
  hosts: [{ host: ENV['ES_ADDRESS'], port: port }],
  transport_options: { request: { timeout: 200 } },
}

Elasticsearch::Model.client = Elasticsearch::Client.new(config) if Rails.env != 'test'
