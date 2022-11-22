import typesense


client = typesense.Client(
    {
        "api_key": "brandheat123123",
        "nodes": [{"host": "13.212.76.211", "port": "8108", "protocol": "http"}],
        "connection_timeout_seconds": 20,
    }
)
client.collections['fb_all'].delete()
client.collections['fb_post'].delete()

# search_parameters = {
#     "q": "Nhân viên",
#     "query_by": "title",
#     "sort_by": "last_update:desc",
#     "max_hits": "50",
# }
# print(client.collections["news"].documents.search(search_parameters))
