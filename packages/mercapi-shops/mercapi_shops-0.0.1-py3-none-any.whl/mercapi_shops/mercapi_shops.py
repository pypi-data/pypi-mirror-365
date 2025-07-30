# mercapi_shops/mercapi_shops.py
# -*- coding: utf-8 -*-
"""
Enterprise-seller (mercari-shops.com) async client.

Example
-------
    from mercapi_shops import MercapiShops
    api = MercapiShops()
    res = await api.search("アゾン", shop_id="d2uUKgmbjTGT7BzBGUnXxe")
"""
from __future__ import annotations

import httpx, logging
from typing import Optional, Dict

from mercapi_shops.requests import ShopsSearchRequestData
from mercapi_shops.mapping  import map_to_class
from mercapi_shops.models   import ShopSearchResults

log = logging.getLogger(__name__)

class MercapiShops:
    GRAPHQL_URL = "https://mercari-shops.com/graphql"
    SEARCH_QUERY = """
    query SearchTop($search: ProductSearchCriteria!, $cursor: String, $shopIds: [String!]) {
      products(search: $search, after: $cursor, shopIds: $shopIds, first: 100){
        pageInfo { hasNextPage endCursor }
        edges    { node { id name price inStock assets { imageUrl } } }
      }
    }
    """

    def __init__(
        self,
        *,
        proxies: Optional[Dict[str, str]] = None,
        user_agent: str = "Mozilla/5.0",
        cookies: Optional[Dict[str, str]] = None,
    ) -> None:
        self._client  = httpx.AsyncClient(proxies=proxies, cookies=cookies or {})
        self._headers = {
            "User-Agent":       user_agent,
            "Referer":          "https://mercari-shops.com/",
            "Content-Type":     "application/json; charset=utf-8",
            "x-data-fetch-for": "csr",
            "Accept":           "application/json",  # === NEW: 兼容性更好
        }

    # ───────── public API ─────────
    async def search(
        self,
        keyword: str,
        *,
        shop_id: str,
        cursor: str = "",
        in_stock: Optional[bool] = None,       # 保持你上版新增的参数
        order_by: Optional[str] = None,        # 保持你上版新增的参数
    ) -> ShopSearchResults:
        req = ShopsSearchRequestData(keyword, shop_id, cursor, in_stock=in_stock, order_by=order_by)
        res = await self._post_graphql(req)
        return res

    async def _post_graphql(self, req: ShopsSearchRequestData) -> ShopSearchResults:
        payload = {
            "query":          self.SEARCH_QUERY,
            "operationName":  "SearchTop",   # === NEW: 明确 operationName（有些后端偏好）
            "variables":      req.data,
        }
        r = await self._client.post(
            self.GRAPHQL_URL,
            json=payload,
            headers=self._headers,
            timeout=(5, 60),
        )
        # 如果返回 4xx/5xx，先打印 body 便于排错，再抛异常
        try:
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            # 打印少量上下文，避免污染日志
            body = r.text[:500]
            log.error("GraphQL HTTP error: %s, body=%s", e, body)
            raise

        j = r.json()
        if "errors" in j:
            # GraphQL 语义错误：抛出以便外层重试逻辑接手
            raise RuntimeError(j["errors"])
        res = map_to_class(j["data"]["products"], ShopSearchResults)

        # 保持分页可用
        res._request = req          # for next_page()
        res._request._api = self    # weak ref back to api

        # 兜底过滤/排序（createdAt 已不请求，CREATED_AT 依赖后端排序）
        items = list(res.items) if res.items else []

        if req.in_stock is True:
            items = [i for i in items if getattr(i, "inStock", None) is True]
        elif req.in_stock is False:
            items = [i for i in items if getattr(i, "inStock", None) is False]

        if req.order_by == "PRICE_ASC":
            items.sort(key=lambda x: (getattr(x, "price", None) is None, getattr(x, "price", None)))
        elif req.order_by == "PRICE_DESC":
            items.sort(key=lambda x: (getattr(x, "price", None) is None, getattr(x, "price", None)), reverse=True)
        # elif req.order_by == "CREATED_AT":  # 不做本地兜底，交给后端

        res.items = items
        return res

    async def __aenter__(self):  # optional context-manager
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._client.aclose()
