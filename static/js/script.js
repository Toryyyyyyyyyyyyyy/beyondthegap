// 简单的交互功能

document.addEventListener('DOMContentLoaded', function() {
    // 图片预览功能
    const imageInput = document.getElementById('image');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();

                reader.onload = function(e) {
                    // 检查是否已有预览图
                    let previewContainer = document.querySelector('.image-preview');
                    if (!previewContainer) {
                        previewContainer = document.createElement('div');
                        previewContainer.className = 'image-preview';
                        imageInput.parentNode.appendChild(previewContainer);
                    }

                    previewContainer.innerHTML = `
                        <p>图片预览:</p>
                        <img src="${e.target.result}" alt="图片预览" style="max-width: 200px; border-radius: 4px; margin-top: 10px;">
                    `;
                };

                reader.readAsDataURL(file);
            }
        });
    }

    // 删除确认增强
    const deleteButtons = document.querySelectorAll('.btn-icon.delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('确定要删除这项内容吗？此操作无法撤销。')) {
                e.preventDefault();
            }
        });
    });

    // 表单验证
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = '#dc3545';

                    // 添加错误提示
                    let errorMsg = field.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('error-message')) {
                        errorMsg = document.createElement('div');
                        errorMsg.className = 'error-message';
                        errorMsg.style.color = '#dc3545';
                        errorMsg.style.fontSize = '0.9rem';
                        errorMsg.style.marginTop = '0.25rem';
                        field.parentNode.appendChild(errorMsg);
                    }
                    errorMsg.textContent = '此字段为必填项';
                } else {
                    field.style.borderColor = '#ced4da';

                    // 移除错误提示
                    const errorMsg = field.nextElementSibling;
                    if (errorMsg && errorMsg.classList.contains('error-message')) {
                        errorMsg.remove();
                    }
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('请填写所有必填字段！');
            }
        });
    });

    // 简单的主题切换（示例功能）
    const themeToggle = document.createElement('button');
    themeToggle.textContent = 'Change Theme';
    themeToggle.className = 'btn secondary';
    themeToggle.style.position = 'fixed';
    themeToggle.style.bottom = '20px';
    themeToggle.style.right = '20px';
    themeToggle.style.zIndex = '1000';

    themeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');

        if (document.body.classList.contains('dark-mode')) {
            document.body.style.backgroundColor = '#343a40';
            document.body.style.color = '#f8f9fa';
            themeToggle.textContent = 'Light Mode';
        } else {
            document.body.style.backgroundColor = '';
            document.body.style.color = '';
            themeToggle.textContent = 'Dark Mode';
        }
    });

    document.body.appendChild(themeToggle);
});
