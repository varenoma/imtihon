from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from core.database import get_db
from models.menu import Menu, SubMenu
from schemas.menu import MenuCreate, MenuUpdate, MenuOut, SubMenuCreate, SubMenuUpdate, SubMenuOut, PaginatedMenuOut
from auth.dependencies import get_current_admin

router = APIRouter(prefix="/menus", tags=["Menular"])


@router.get("/", response_model=PaginatedMenuOut)
async def get_all(
    db: AsyncSession = Depends(get_db),
    page: int = Query(
        1, ge=1, description="Sahifa raqami, 1 dan kam bo'lmasligi kerak."),
    per_page: int = Query(
        10, ge=1, le=100, description="Har bir sahifadagi elementlar soni, 1-100 oralig'ida.")
):
    try:
        # Umumiy elementlar sonini hisoblash
        total_query = await db.execute(select(func.count()).select_from(Menu))
        total = total_query.scalar()

        # Sahifalash uchun ma'lumotlarni olish
        offset = (page - 1) * per_page
        result = await db.execute(
            select(Menu).offset(offset).limit(per_page).order_by(Menu.id)
        )
        items = result.scalars().all()

        # Umumiy sahifalar sonini hisoblash
        total_pages = (total + per_page - 1) // per_page

        return PaginatedMenuOut(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ma'lumotlarni olishda xato yuz berdi: {str(e)}"
        )


@router.post("/for_admin/", response_model=MenuOut)
async def create_menu(
    menu: MenuCreate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        new_menu = Menu(
            title=menu.title,
            url=menu.url
        )
        db.add(new_menu)
        await db.commit()
        await db.refresh(new_menu)
        return new_menu
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Menu yaratishda xato yuz berdi: {str(e)}"
        )


@router.put("/{id}/for_admin/", response_model=MenuOut)
async def update_menu(
    id: int,
    menu: MenuUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        result = await db.execute(select(Menu).where(Menu.id == id))
        db_menu = result.scalar_one_or_none()
        if not db_menu:
            raise HTTPException(status_code=404, detail="Menu topilmadi")

        if menu.title is not None:
            db_menu.title = menu.title
        if menu.url is not None:
            db_menu.url = menu.url

        await db.commit()
        await db.refresh(db_menu)
        return db_menu
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Menu yangilashda xato yuz berdi: {str(e)}"
        )


@router.delete("/{id}/for_admin/")
async def delete_menu(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        result = await db.execute(select(Menu).where(Menu.id == id))
        db_menu = result.scalar_one_or_none()
        if not db_menu:
            raise HTTPException(status_code=404, detail="Menu topilmadi")

        await db.delete(db_menu)
        await db.commit()
        return {"message": "Menu va unga tegishli submenular muvaffaqiyatli o'chirildi"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Menu o'chirishda xato yuz berdi: {str(e)}"
        )


@router.post("/submenus/for_admin/", response_model=SubMenuOut)
async def create_submenu(
    submenu: SubMenuCreate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        # Menu mavjudligini tekshirish
        result = await db.execute(select(Menu).where(Menu.id == submenu.menu_id))
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=404, detail="Bog'langan menu topilmadi")

        new_submenu = SubMenu(
            title=submenu.title,
            url=submenu.url,
            menu_id=submenu.menu_id
        )
        db.add(new_submenu)
        await db.commit()
        await db.refresh(new_submenu)
        return new_submenu
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Submenu yaratishda xato yuz berdi: {str(e)}"
        )


@router.put("/submenus/{id}/for_admin/", response_model=SubMenuOut)
async def update_submenu(
    id: int,
    submenu: SubMenuUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        result = await db.execute(select(SubMenu).where(SubMenu.id == id))
        db_submenu = result.scalar_one_or_none()
        if not db_submenu:
            raise HTTPException(status_code=404, detail="Submenu topilmadi")

        if submenu.title is not None:
            db_submenu.title = submenu.title
        if submenu.url is not None:
            db_submenu.url = submenu.url
        if submenu.menu_id is not None:
            result = await db.execute(select(Menu).where(Menu.id == submenu.menu_id))
            if not result.scalar_one_or_none():
                raise HTTPException(
                    status_code=404, detail="Bog'langan menu topilmadi")
            db_submenu.menu_id = submenu.menu_id

        await db.commit()
        await db.refresh(db_submenu)
        return db_submenu
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Submenu yangilashda xato yuz berdi: {str(e)}"
        )


@router.delete("/submenus/{id}/for_admin/")
async def delete_submenu(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        result = await db.execute(select(SubMenu).where(SubMenu.id == id))
        db_submenu = result.scalar_one_or_none()
        if not db_submenu:
            raise HTTPException(status_code=404, detail="Submenu topilmadi")

        await db.delete(db_submenu)
        await db.commit()
        return {"message": "Submenu muvaffaqiyatli o'chirildi"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Submenu o'chirishda xato yuz berdi: {str(e)}"
        )
