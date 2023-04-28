import os
import sys
import socket
import dns.resolver
from urllib import request as urlrequest

if __name__ == "__main__":

  google_dns_ip = "8.8.8.8"        # That is Google's public DNS server
  host = 'google.com'
  url = 'https://' + host

  # First try using hostname dns resolution
  resolver_ = dns.resolver.Resolver()
  answer = resolver_.resolve(host,'A')
  for rdata in answer:
    print('Testing DNS: hostname', host, 'resolved to ip number', rdata.to_text(), ': OK.')

  # Is the DNS host visible from this container ?
  # The following snipet comes from
  # https://stackoverflow.com/questions/3764291/how-can-i-see-if-theres-an-available-and-active-network-connection-in-python
  port = 53  # (tcp) is dns service
  timeout = 10
  try:
      socket.setdefaulttimeout(timeout)
      socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((google_dns_ip, port))
      print('Socket connection to', google_dns_ip + ':' + str(port) + ': OK')
  except socket.error as err:
      print('Socket connection to', google_dns_ip + ':' + str(port) + ': FAILED')
      print("   Error raised ", err)

  # We now have IP connectivity and DNS service. Let's make and http request
  # just in case e.g. some http proxy is required
  req = urlrequest.Request(url)
  if os.environ.get('HTTP_PROXY'):
    http_proxy_host = os.environ["HTTP_PROXY"]
    http_proxy_host = http_proxy_host.removeprefix("http://")
    req.set_proxy(http_proxy_host, "http")
    print("Using http proxy: ", http_proxy_host)
  else:
    print("No http proxy server found in environment.")
  if os.environ.get('HTTPS_PROXY'):
    https_proxy_host = os.environ["HTTPS_PROXY"]
    https_proxy_host = https_proxy_host.removeprefix("http://")
    https_proxy_host = https_proxy_host.removeprefix("https://") # Just in case
    req.set_proxy(https_proxy_host, "https")
    print("Using https proxy: ", https_proxy_host)
  else:
    print("No httpS proxy server found in environment.")
  
  try:
      print("Trying to request url ", url, ":", end="")
      response = urlrequest.urlopen(req)
      print(" OK.")
  except urlrequest.URLError as err:
      print(" FAILED.")
      print("Try configuring an http(s) proxy ?")
      sys.exit(1)
