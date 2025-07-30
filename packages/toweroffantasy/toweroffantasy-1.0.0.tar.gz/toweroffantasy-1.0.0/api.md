# Auth

Types:

```python
from toweroffantasy.types import LoginResponse
```

Methods:

- <code title="patch /auth/change-password">client.auth.<a href="./src/toweroffantasy/resources/auth.py">change_password</a>(\*\*<a href="src/toweroffantasy/types/auth_change_password_params.py">params</a>) -> None</code>
- <code title="get /auth/check">client.auth.<a href="./src/toweroffantasy/resources/auth.py">check_access_token</a>() -> object</code>
- <code title="post /auth/login">client.auth.<a href="./src/toweroffantasy/resources/auth.py">login</a>(\*\*<a href="src/toweroffantasy/types/auth_login_params.py">params</a>) -> <a href="./src/toweroffantasy/types/login_response.py">LoginResponse</a></code>
- <code title="post /auth/register">client.auth.<a href="./src/toweroffantasy/resources/auth.py">register</a>(\*\*<a href="src/toweroffantasy/types/auth_register_params.py">params</a>) -> <a href="./src/toweroffantasy/types/login_response.py">LoginResponse</a></code>

# Users

Types:

```python
from toweroffantasy.types import UserMe, UserRetrieveByIDResponse
```

Methods:

- <code title="get /users/{user_id}">client.users.<a href="./src/toweroffantasy/resources/users.py">retrieve_by_id</a>(user_id) -> <a href="./src/toweroffantasy/types/user_retrieve_by_id_response.py">UserRetrieveByIDResponse</a></code>
- <code title="get /users/@me">client.users.<a href="./src/toweroffantasy/resources/users.py">retrieve_me</a>() -> <a href="./src/toweroffantasy/types/user_me.py">UserMe</a></code>

# Simulacra

Types:

```python
from toweroffantasy.types import (
    ImitationAssets,
    LangsEnum,
    SimulacrumGift,
    SimulacraRetrieveResponse,
    SimulacraListResponse,
    SimulacraLikedGiftsResponse,
)
```

Methods:

- <code title="get /simulacra/{simulacrum_id}">client.simulacra.<a href="./src/toweroffantasy/resources/simulacra.py">retrieve</a>(simulacrum_id, \*\*<a href="src/toweroffantasy/types/simulacra_retrieve_params.py">params</a>) -> <a href="./src/toweroffantasy/types/simulacra_retrieve_response.py">SimulacraRetrieveResponse</a></code>
- <code title="get /simulacra">client.simulacra.<a href="./src/toweroffantasy/resources/simulacra.py">list</a>(\*\*<a href="src/toweroffantasy/types/simulacra_list_params.py">params</a>) -> <a href="./src/toweroffantasy/types/simulacra_list_response.py">SimulacraListResponse</a></code>
- <code title="get /simulacra/{simulacrum_id}/gifts">client.simulacra.<a href="./src/toweroffantasy/resources/simulacra.py">liked_gifts</a>(simulacrum_id, \*\*<a href="src/toweroffantasy/types/simulacra_liked_gifts_params.py">params</a>) -> <a href="./src/toweroffantasy/types/simulacra_liked_gifts_response.py">SimulacraLikedGiftsResponse</a></code>

# Matrices

Types:

```python
from toweroffantasy.types import (
    MatriceAssets,
    SuitAssets,
    MatrixRetrieveResponse,
    MatrixListResponse,
)
```

Methods:

- <code title="get /matrices/{matrix_id}">client.matrices.<a href="./src/toweroffantasy/resources/matrices.py">retrieve</a>(matrix_id, \*\*<a href="src/toweroffantasy/types/matrix_retrieve_params.py">params</a>) -> <a href="./src/toweroffantasy/types/matrix_retrieve_response.py">MatrixRetrieveResponse</a></code>
- <code title="get /matrices">client.matrices.<a href="./src/toweroffantasy/resources/matrices.py">list</a>(\*\*<a href="src/toweroffantasy/types/matrix_list_params.py">params</a>) -> <a href="./src/toweroffantasy/types/matrix_list_response.py">MatrixListResponse</a></code>

# Weapons

Types:

```python
from toweroffantasy.types import (
    Assets,
    Category,
    Element,
    ShatterOrCharge,
    WeaponRetrieveResponse,
    WeaponListResponse,
)
```

Methods:

- <code title="get /weapons/{weapon_id}">client.weapons.<a href="./src/toweroffantasy/resources/weapons.py">retrieve</a>(weapon_id, \*\*<a href="src/toweroffantasy/types/weapon_retrieve_params.py">params</a>) -> <a href="./src/toweroffantasy/types/weapon_retrieve_response.py">WeaponRetrieveResponse</a></code>
- <code title="get /weapons">client.weapons.<a href="./src/toweroffantasy/resources/weapons.py">list</a>(\*\*<a href="src/toweroffantasy/types/weapon_list_params.py">params</a>) -> <a href="./src/toweroffantasy/types/weapon_list_response.py">WeaponListResponse</a></code>

# Banners

Types:

```python
from toweroffantasy.types import Banner, BannerListResponse, BannerRetrieveCurrentResponse
```

Methods:

- <code title="post /banners">client.banners.<a href="./src/toweroffantasy/resources/banners.py">create</a>(\*\*<a href="src/toweroffantasy/types/banner_create_params.py">params</a>) -> <a href="./src/toweroffantasy/types/banner.py">Banner</a></code>
- <code title="get /banners">client.banners.<a href="./src/toweroffantasy/resources/banners.py">list</a>(\*\*<a href="src/toweroffantasy/types/banner_list_params.py">params</a>) -> <a href="./src/toweroffantasy/types/banner_list_response.py">BannerListResponse</a></code>
- <code title="get /banners/current">client.banners.<a href="./src/toweroffantasy/resources/banners.py">retrieve_current</a>() -> <a href="./src/toweroffantasy/types/banner_retrieve_current_response.py">BannerRetrieveCurrentResponse</a></code>

# Gifts

Types:

```python
from toweroffantasy.types import Gift, GiftListResponse
```

Methods:

- <code title="get /gifts/{gift_id}">client.gifts.<a href="./src/toweroffantasy/resources/gifts.py">retrieve</a>(gift_id, \*\*<a href="src/toweroffantasy/types/gift_retrieve_params.py">params</a>) -> <a href="./src/toweroffantasy/types/gift.py">Gift</a></code>
- <code title="get /gifts">client.gifts.<a href="./src/toweroffantasy/resources/gifts.py">list</a>(\*\*<a href="src/toweroffantasy/types/gift_list_params.py">params</a>) -> <a href="./src/toweroffantasy/types/gift_list_response.py">GiftListResponse</a></code>

# Mounts

Types:

```python
from toweroffantasy.types import MountAssets, MountRetrieveResponse, MountListResponse
```

Methods:

- <code title="get /mounts/{mount_id}">client.mounts.<a href="./src/toweroffantasy/resources/mounts.py">retrieve</a>(mount_id, \*\*<a href="src/toweroffantasy/types/mount_retrieve_params.py">params</a>) -> <a href="./src/toweroffantasy/types/mount_retrieve_response.py">MountRetrieveResponse</a></code>
- <code title="get /mounts">client.mounts.<a href="./src/toweroffantasy/resources/mounts.py">list</a>(\*\*<a href="src/toweroffantasy/types/mount_list_params.py">params</a>) -> <a href="./src/toweroffantasy/types/mount_list_response.py">MountListResponse</a></code>

# Health

Types:

```python
from toweroffantasy.types import HealthCheckResponse
```

Methods:

- <code title="get /health">client.health.<a href="./src/toweroffantasy/resources/health.py">check</a>() -> <a href="./src/toweroffantasy/types/health_check_response.py">HealthCheckResponse</a></code>

# Ping

Types:

```python
from toweroffantasy.types import PingPingResponse
```

Methods:

- <code title="get /ping">client.ping.<a href="./src/toweroffantasy/resources/ping.py">ping</a>() -> <a href="./src/toweroffantasy/types/ping_ping_response.py">PingPingResponse</a></code>

# Version

Types:

```python
from toweroffantasy.types import VersionRetrieveResponse
```

Methods:

- <code title="get /version">client.version.<a href="./src/toweroffantasy/resources/version.py">retrieve</a>() -> <a href="./src/toweroffantasy/types/version_retrieve_response.py">VersionRetrieveResponse</a></code>
