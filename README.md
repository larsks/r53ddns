This will update a given record in Route53 DNS with the ip address of
the connecting client.

## Updating a record

If your dynamic host is `foo.example.com`, you could update the DNS
record with something like this:

    curl https://r53ddns.example.com/update/foo.example.com?secret=mysecret

