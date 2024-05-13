const swiper = new Swiper('.swiper', {
    direction: 'horizontal',
    loop: true,
    autoplay: {
        delay: 3000,
    },
    speed: 2000,
    effect: "coverflow",
    coverflowEffect: {
        rotate: 3,
        stretch: 2,
        depth: 100,
        modifier: 5,
        slideShadows: false,
    },
    pagination: {
        el: '.swiper-pagination',
    },

    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
    },
});


let cartBtn = document.querySelector('.cart-button');
let body = document.querySelector('body');
let closeBtn = document.querySelector('.close');
let cart = document.querySelector('.cart');

cartBtn.addEventListener('click', () => {
    body.classList.add("show-cart");
    renderCart();
});

closeBtn.addEventListener('click', () => {
    body.classList.remove("show-cart");
});

body.addEventListener('click', e => {
    if (!cart.contains(e.target) && !cartBtn.contains(e.target)){
        body.classList.remove("show-cart");
    }
});


let addToCartBtn = document.querySelectorAll('.card-button');
let cartList = [];

addToCartBtn.forEach(btn => {
    btn.addEventListener('click', () => {
        let product = btn.parentElement.parentElement.parentElement.parentElement;
        let productInfo = {
            id: product.querySelector('.card-img > img').dataset.id,
            image: product.querySelector('.card-img > img').src,
            name: product.querySelector('.card-title > h3').textContent,
            price: parseFloat(product.querySelector('.card-price').textContent.split(' ')[0]),
            quantity: 1
        };
        if (cartList.some(item => item.id === productInfo.id)) {
            cartList.forEach(item => {
                if (item.id === productInfo.id) {
                    item.quantity++;
                }
            });
            renderCart();
            return;
        }
        cartList.push(productInfo);
        renderCart();
    });
});

const total = document.querySelector('.cartDetails > h2 > span');
const renderCart = () => {
    let cartListHTML = document.querySelector('.cartItems');
    cartListHTML.innerHTML = '';
    cartList.forEach(product => {
        let li = document.createElement('li');
        li.innerHTML = `
            <img src="${product.image}" data-id="${product.id}" alt="">
            <div class="quantityNamePrice">
                <h3>${product.name}</h3>
                <p>${product.price} $</p>
            </div>
            <div class="quantityRemove">
                <button class="minus">-</button>
                <input type="number" min="1" value="${product.quantity}" class="quantity-input" disabled>
                <button class="plus">+</button>
            </div>
            <button class="remove">X</button>
        `;
        li.querySelector('.remove').addEventListener('click', (e) => {
            e.preventDefault();
            li.classList.add('animate-out');

            setTimeout(() => {
                cartList = cartList.filter(item => item.id !== product.id);
                renderCart();
            }, 800);
        });
        li.querySelector('.minus').addEventListener('click', (e) => {
            e.stopPropagation();
            if (product.quantity > 1) {
                product.quantity--;
                renderCart();
            }
        }, true);

        li.querySelector('.plus').addEventListener('click', (e) => {
            e.stopPropagation();
            product.quantity++;
            renderCart();
        }, true);
        cartListHTML.appendChild(li);
    });
    cartList.length === 0 ? total.textContent = 0 : total.textContent = cartList.reduce((acc, item) => acc + item.price * item.quantity, 0).toFixed(2);
    localStorage.setItem('cart', JSON.stringify(cartList));
    document.querySelector(".cart-number").textContent = cartList.length;
};

const menuBar = document.querySelectorAll('.menu-categories > ul > li');

const cards = document.querySelectorAll('.card');

menuBar.forEach(menu => {
    menu.addEventListener('click', () => {
        menuBar.forEach(item => {
            item.classList.remove('active');
        });
        menu.classList.add('active');
        cards.forEach(card => {
            card.style.display = "none";
            if (menu.textContent === "All") {
                card.style.display = "block";
            } else if (card.dataset.cat === menu.textContent.toLowerCase()) {
                card.style.display = "block";
            }
        });
    });
});


const mobileToggleBtn = document.querySelector('.menu-toggle');
const mobileMenu = document.querySelector('.mobileMenuBar');

mobileToggleBtn.addEventListener('click', () => {
    if (mobileMenu.classList.contains('showMenu')) {
        mobileMenu.classList.remove('showMenu');
        body.style.overflow = 'auto';
    } else {
        mobileMenu.classList.add('showMenu');
        body.style.overflow = 'hidden';
    }
});


document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('cart')) {
        cartList = JSON.parse(localStorage.getItem('cart'));
        renderCart();
    }

    const checkoutBtn = document.querySelector('.checkout');
    checkoutBtn.addEventListener('click', () => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/checkout', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(cartList));
    });

    var checkoutConfirm = document.querySelector('.checkoutConfirm');
    if (checkoutConfirm !== null) {
        checkoutConfirm.addEventListener('click', () => {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/confirm', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify({"message": "success"}));
        });
    }
});