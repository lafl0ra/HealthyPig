var language = {
    en: {
        logo: "Healthy-Pig",
        navprofile: "I'm, {{ user.username }}",
        navmain: "<b>Main</b>",
        navprogress: "<b>Progress</b>",
        hello: "Hello {{ user.username }}",
        descriptionhello: "This is your report for today.",
        piechart1: "today",
        piechart2: 'kcal from <span class="text-danger">{{ user_profile.TDEE }}</span> kcal goal',
        piechart3: "Calories consumed from food",
        piechart4: "Calories burned from exercise",
        food1: "Add your foods",
        searchPlaceholder: "Search Menu/Ingredient",
        searchButton: "Search",
        food2: "Add New Menu",
        foodname: "Name",
        foodcal: "Calories",
        foodquantity: "Quantity in grams",
        foodowner: "Creator",
        foodchoose: "Choose",
        ex1: "Add your exercises",
        searchPlaceholder2: "Search Exercise",
        searchButton2: "Search",
        exname: "Name",
        excalmin: "Calories (Per Minute)",
        excalhr: "Calories (Per Hour)",
        exchoose: "Choose",
        navlogout: "Logout",
        fooddetaildes: "Description :",
    },
    th: {
        logo: "หมูแข็งแรง",
        navprofile: "ฉันคือ {{ user.username }}",
        navmain: "<b>หน้าหลัก</b>",
        navprogress: "<b>ความคืบหน้า</b>",
        hello: "สวัสดี {{ user.username }}",
        descriptionhello: "นี่คือรายงานของคุณสำหรับวันนี้",
        piechart1: "วันนี้",
        piechart2: 'แคลอรีจากเป้าหมาย <span class="text-danger">{{ user_profile.TDEE }}</span> แคลอรี',
        piechart3: "แคลอรี่ที่ได้รับจากอาหาร",
        piechart4: "แคลอรี่ที่เผาผลาญจากการออกกำลังกาย",
        food1: "เพิ่มอาหารของคุณ",
        searchPlaceholder: "ค้นหาเมนู/ส่วนผสม",
        searchButton: "ค้นหา",
        food2: "เพิ่มเมนูใหม่",
        foodname: "ชื่อ",
        foodcal: "แคลอรี่",
        foodquantity: "ปริมาณ (กรัม)",
        foodowner: "ผู้คิดค้น",
        foodchoose: "เลือก",
        ex1: "เพิ่มการออกกำลังกายของคุณ",
        searchPlaceholder2: "ค้นหาการออกกำลังกาย",
        searchButton2: "ค้นหา",
        exname: "ชื่อ",
        excalmin: "แคลอรี่ (ต่อนาที)",
        excalhr: "แคลอรี่ (ต่อชั่วโมง)",
        exchoose: "เลือก",
        navlogout: "ออกจากระบบ",
        fooddetaildes: "คำอธิบาย :",
    },
};

// ฟังก์ชันเพื่อเปลี่ยนภาษา
function changeLanguage(lang) {
    localStorage.setItem('preferredLanguage', lang);
    document.getElementById("logo").innerText = language[lang].logo;
    document.getElementById("navprofile").innerText = language[lang].navprofile;
    document.getElementById("navmain").innerHTML = language[lang].navmain;
    document.getElementById("navprogress").innerHTML = language[lang].navprogress;
    document.getElementById("navlogout").innerHTML = language[lang].navlogout;
    document.getElementById("hello").innerText = language[lang].hello;
    document.getElementById("descriptionhello").innerText = language[lang].descriptionhello;
    document.getElementById("piechart1").innerText = language[lang].piechart1;
    document.getElementById("piechart2").innerHTML = language[lang].piechart2;
    document.getElementById("piechart3").innerText = language[lang].piechart3;
    document.getElementById("piechart4").innerText = language[lang].piechart4;
    document.getElementById("food1").innerText = language[lang].food1;

    // อัปเดตการค้นหาอาหาร
    document.querySelector(".input-search").setAttribute("placeholder", language[lang].searchPlaceholder);
    document.querySelector(".button-search").setAttribute("value", language[lang].searchButton);
    document.getElementById("food2").innerText = language[lang].food2;
    document.getElementById("foodname").innerText = language[lang].foodname;
    document.getElementById("foodcal").innerText = language[lang].foodcal;
    document.getElementById("foodquantity").innerText = language[lang].foodquantity;
    document.getElementById("foodowner").innerText = language[lang].foodowner;

    // อัปเดตปุ่ม "Choose"
    var chooseElements = document.querySelectorAll(".foodchoose");
    chooseElements.forEach(function (element) {
        element.innerText = language[lang].foodchoose;
    });

    // อัปเดตการค้นหาการออกกำลังกาย
    document.querySelector(".input-search2").setAttribute("placeholder", language[lang].searchPlaceholder2);
    document.querySelector(".button-search2").setAttribute("value", language[lang].searchButton2);

    // อัปเดตส่วนที่เกี่ยวกับการออกกำลังกาย
    document.getElementById("ex1").innerText = language[lang].ex1;
    document.getElementById("exname").innerText = language[lang].exname;
    document.getElementById("excalmin").innerText = language[lang].excalmin;
    document.getElementById("excalhr").innerText = language[lang].excalhr;

    // อัปเดตปุ่ม "Choose" สำหรับการออกกำลังกาย
    var exChooseElements = document.querySelectorAll(".exchoose");
    exChooseElements.forEach(function (element) {
        element.innerText = language[lang].exchoose;
    });

    document.getElementById("fooddetaildes").innerText = language[lang].fooddetaildes;
}

// โหลดภาษาจาก localStorage เมื่อหน้าโหลด
window.onload = function() {
    const preferredLanguage = localStorage.getItem('preferredLanguage') || 'en'; // ค่าเริ่มต้นเป็นภาษาอังกฤษ
    changeLanguage(preferredLanguage);
};

// ตั้งค่าปุ่มให้เปลี่ยนภาษา
document.querySelectorAll("[data-reload]").forEach(button => {
    button.onclick = function () {
        changeLanguage(this.getAttribute("data-reload"));
        location.reload(); // ทำการโหลดหน้าใหม่หลังจากเปลี่ยนภาษา
    };
});