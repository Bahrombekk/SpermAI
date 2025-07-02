#!/bin/bash
cd ~/Desktop/SpermAI
git add .

git commit -m "Avtomatik push: $(date)" || {
    echo "Hech qanday o'zgarish yo'q yoki commitda xato yuz berdi."
    exit 1
}

# Uzoqdagi branch bilan sinxronlash
git pull origin main --rebase || {
    echo "Git pull (rebase) xatoligi. Konflikt bo'lishi mumkin."
    exit 1
}

git push origin main || {
    echo "Push qilishda xato yuz berdi. Autentifikatsiyani tekshiring yoki git pull qiling."
    exit 1
}

echo "Barcha o'zgarishlar GitHub-ga muvaffaqiyatli yuklandi!"
