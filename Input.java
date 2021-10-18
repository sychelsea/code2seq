private List createList(String redirectURL, String content, List retHeaderList) {
    List list = new HashList();
    list.put(headerKey, retHeaderList);
    if (redirectURL != null) {
        list.put(URLKey, redirectURL);
    } else if (content != null) {
        list.put(responseDataKey, content);
    }
    return list;
}


