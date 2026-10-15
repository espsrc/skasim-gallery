// Shared by every case page: builds the contents sidebar and the previous/next links.
// Adding a case: append it to CASES (order = gallery order).
const CASES = [
    { dir: "case1-mightee", title: "MIGHTEE deep field" },
    { dir: "case2-polarization", title: "Circular polarization in the confusion limit" },
    { dir: "case3-staged-delivery", title: "SKAO staged delivery" },
    { dir: "case4-redshift-galaxies", title: "Redshifted radio galaxies" },
    { dir: "case5-hi-kinematics", title: "HI gas kinematics in spiral galaxies" },
];

(function () {
    const main = document.querySelector("main");
    if (!main) return;

    // contents sidebar from the section headings
    const heads = Array.from(main.querySelectorAll(".case-block > h2"));
    const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
    const toc = document.createElement("nav");
    toc.className = "toc";
    toc.setAttribute("aria-label", "On this page");
    toc.innerHTML = '<p class="toc-title">On this page</p><ol></ol>';
    const list = toc.querySelector("ol");
    const links = heads.map((h) => {
        if (!h.id) h.id = slug(h.textContent);
        const li = document.createElement("li");
        const a = document.createElement("a");
        a.href = "#" + h.id;
        a.textContent = h.dataset.toc || h.textContent;
        li.appendChild(a);
        list.appendChild(li);
        return a;
    });
    main.prepend(toc);

    // highlight the section being read
    const setActive = (id) =>
        links.forEach((a) => a.classList.toggle("active", a.hash === "#" + id));
    const observer = new IntersectionObserver(
        (entries) => {
            const visible = entries.filter((e) => e.isIntersecting);
            if (visible.length) setActive(visible[0].target.querySelector("h2").id);
        },
        { rootMargin: "-90px 0px -60% 0px" },
    );
    heads.forEach((h) => observer.observe(h.parentElement));

    // previous / next case
    const here = CASES.findIndex((c) => location.pathname.includes("/" + c.dir + "/"));
    if (here < 0) return;
    const pager = document.createElement("nav");
    pager.className = "case-pager";
    pager.setAttribute("aria-label", "More cases");
    const link = (c, cls, label) =>
        `<a class="${cls}" href="../${c.dir}/index.html"><small>${label}</small><span>${c.title}</span></a>`;
    const prev = CASES[here - 1], next = CASES[here + 1];
    pager.innerHTML =
        (prev ? link(prev, "prev", `← Case #${here}`) : "") +
        (next ? link(next, "next", `Case #${here + 2} →`) : "");
    main.appendChild(pager);
})();
