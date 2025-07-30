"""Menu items."""

from nautobot.apps.ui import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuTab

items = (
    NavMenuItem(
        link="plugins:frame_surfer:frametv_list",
        name="Frame TVs",
        permissions=["frame_surfer.view_frametv"],
        buttons=(
            NavMenuAddButton(
                link="plugins:frame_surfer:frametv_add",
                permissions=["frame_surfer.add_frametv"],
            ),
        ),
    ),
    NavMenuItem(
        link="plugins:frame_surfer:unsplashmodel_list",
        name="Unsplash",
        permissions=["frame_surfer.view_unsplashmodel"],
        buttons=(
            NavMenuAddButton(
                link="plugins:frame_surfer:unsplashmodel_add",
                permissions=["frame_surfer.add_unsplashmodel"],
            ),
        ),
    ),
    NavMenuItem(
        link="plugins:frame_surfer:photomodel_list",
        name="Photos",
        permissions=["frame_surfer.view_photomodel"],
        buttons=(
            NavMenuAddButton(
                link="plugins:frame_surfer:photomodel_add",
                permissions=["frame_surfer.add_photomodel"],
            ),
        ),
    ),
)

menu_items = (
    NavMenuTab(
        name="Frame Surfer",
        groups=(NavMenuGroup(name="Frame Surfer", items=tuple(items)),),
    ),
)
