@echo off
echo ========================================
echo 库房出入库管理系统 - 启动脚本
echo ========================================
echo.

echo [1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [2/4] 安装后端依赖...
cd backend
pip install -r requirements.txt -q

echo [3/4] 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Node.js，请先安装Node.js 16+
    pause
    exit /b 1
)

echo [4/4] 安装前端依赖...
cd ..\frontend
call npm install

echo.
echo ========================================
echo 依赖安装完成！
echo ========================================
echo.
echo 启动方式:
echo   后端: cd backend ^&^& python run.py
echo   前端: cd frontend ^&^& npm run dev
echo.
echo 默认账号:
echo   管理员: admin / admin123
echo   操作员: operator / operator123
echo   查看员: viewer / viewer123
echo.
pause
