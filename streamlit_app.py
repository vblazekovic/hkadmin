<!DOCTYPE html>
<html lang="hr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HK Podravka - Administracija</title>
    <!-- Učitavanje Tailwind CSS-a -->
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Postavljanje fonta Inter i prilagodba klupskim bojama */
        :root {
            --hkp-red: #b91c1c; /* Crvena (tamnija) */
            --hkp-gold: #f59e0b; /* Zlatna/Jantarna */
            --hkp-white: #ffffff;
        }
        body { font-family: 'Inter', sans-serif; background-color: #f7f9fb; }
        .card { box-shadow: 0 4px 12px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.05); }
        .tab-button { transition: all 150ms ease-in-out; border-bottom: 2px solid transparent; }
        .tab-active { border-color: var(--hkp-red); color: var(--hkp-red); font-weight: 600; }
        .btn-primary { background-color: var(--hkp-red); color: var(--hkp-white); box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
        .btn-primary:hover { background-color: #9f1212; }
        .btn-secondary { background-color: var(--hkp-gold); color: #1f2937; }
        .btn-secondary:hover { background-color: #d97706; }
    </style>
    <!-- Učitavanje jsPDF (za generiranje dokumenata) - MOCK -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script>
        // Postavljanje globalnih varijabli za Canvas
        const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
        const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : null;
        const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;
    </script>
</head>
<body class="p-4 md:p-8">

    <div id="app" class="max-w-6xl mx-auto">
        
        <header class="text-center mb-8">
            <h1 class="text-5xl font-extrabold mb-2" style="color: var(--hkp-red);">HK PODRAVKA</h1>
            <h2 class="text-xl font-medium text-gray-600">Administracijski Sustav Hrvačkog Kluba</h2>
            <div class="mt-4 p-3 rounded-xl bg-gray-50 border border-gray-200">
                <p class="text-sm font-medium text-gray-700">
                    Korisnički ID: <span id="user-id-display" class="font-mono bg-gray-200 px-2 py-0.5 rounded-md text-xs">Učitavanje...</span>
                </p>
            </div>
        </header>

        <!-- Navigacija za sekcije (Tabs) -->
        <div class="mb-6 overflow-x-auto">
            <nav id="app-tabs" class="flex flex-nowrap border-b border-gray-300">
                <button data-section="klub" class="tab-button py-3 px-4 md:px-6 text-sm whitespace-nowrap tab-active focus:outline-none">O Klubu</button>
                <button data-section="members" class="tab-button py-3 px-4 md:px-6 text-sm whitespace-nowrap text-gray-500 hover:text-gray-700 focus:outline-none">Članovi</button>
                <button data-section="coaches" class="tab-button py-3 px-4 md:px-6 text-sm whitespace-nowrap text-gray-500 hover:text-gray-700 focus:outline-none">Treneri</button>
                <button data-section="groups" class="tab-button py-3 px-4 md:px-6 text-sm whitespace-nowrap text-gray-500 hover:text-gray-700 focus:outline-none">Grupe</button>
                <button data-section="attendance" class="tab-button py-3 px-4 md:px-6 text-sm whitespace-nowrap text-gray-500 hover:text-gray-700 focus:outline-none">Prisustvo</button>
                <button data-section="competitions" class="tab-button py-3 px-4 md:px-6 text-sm whitespace-nowrap text-gray-500 hover:text-gray-700 focus:outline-none">Natjecanja</button>
                <button data-section="statistics" class="tab-button py-3 px-4 md:px-6 text-sm whitespace-nowrap text-gray-500 hover:text-gray-700 focus:outline-none">Statistika</button>
                <button data-section="fees" class="tab-button py-3 px-4 md:px-6 text-sm whitespace-nowrap text-gray-500 hover:text-gray-700 focus:outline-none">Članarine</button>
                <button data-section="comms" class="tab-button py-3 px-4 md:px-6 text-sm whitespace-nowrap text-gray-500 hover:text-gray-700 focus:outline-none">Komunikacija</button>
            </nav>
        </div>

        <!-- Sadržaj sekcija -->
        <div id="sections-container">
            <!-- 1. O KLUBI -->
            <div data-content="klub" class="space-y-6">
                <div class="card bg-white p-6 rounded-xl">
                    <h2 class="text-2xl font-bold mb-4" style="color: var(--hkp-red);">Osnovni Podaci o Klubu</h2>
                    <form id="club-info-form" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="md:col-span-2"><label class="block text-sm font-medium text-gray-700">KLUB (IME)</label><input type="text" id="club-name" value="HRVAČKI KLUB PODRAVKA" disabled class="mt-1 block w-full rounded-md bg-gray-100 p-3 border-gray-300"></div>
                        <div><label class="block text-sm font-medium text-gray-700">Ulica i Kućni Broj</label><input type="text" id="club-address" value="Miklinovec 6a" disabled class="mt-1 block w-full rounded-md bg-gray-100 p-3"></div>
                        <div><label class="block text-sm font-medium text-gray-700">Grad i Poštanski Broj</label><input type="text" id="club-city" value="48000 Koprivnica" disabled class="mt-1 block w-full rounded-md bg-gray-100 p-3"></div>
                        <div><label class="block text-sm font-medium text-gray-700">Email</label><input type="email" id="club-email" value="hsk-podravka@gmail.com" disabled class="mt-1 block w-full rounded-md bg-gray-100 p-3"></div>
                        <div><label class="block text-sm font-medium text-gray-700">OIB</label><input type="text" id="club-oib" value="60911784858" disabled class="mt-1 block w-full rounded-md bg-gray-100 p-3"></div>
                        <div class="md:col-span-2"><label class="block text-sm font-medium text-gray-700">IBAN Račun</label><input type="text" id="club-iban" value="HR6923860021100518154" disabled class="mt-1 block w-full rounded-md bg-gray-100 p-3 font-mono"></div>
                        
                        <h3 class="text-xl font-semibold mt-4 md:col-span-2">Društvene Mreže i Web</h3>
                        <div class="md:col-span-2"><label class="block text-sm font-medium text-gray-700">Web Stranica</label><input type="url" id="club-website" value="hk-podravka.com" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                        <div><label class="block text-sm font-medium text-gray-700">Instagram Link</label><input type="url" id="club-instagram" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                        <div><label class="block text-sm font-medium text-gray-700">Facebook Link</label><input type="url" id="club-facebook" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                        <div><label class="block text-sm font-medium text-gray-700">TikTok Link</label><input type="url" id="club-tiktok" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                        <div class="md:col-span-2 text-right"><button type="submit" class="py-2 px-4 rounded-md btn-secondary">Ažuriraj Linkove</button></div>
                    </form>
                </div>

                <!-- Uprava i Odbori -->
                <div class="card bg-white p-6 rounded-xl">
                    <h2 class="text-2xl font-bold mb-4" style="color: var(--hkp-red);">Uprava Kluba</h2>
                    <p class="text-sm text-gray-500 mb-4">Unesite podatke za predsjednika, tajnika, članove predsjedništva i nadzornog odbora.</p>

                    <div id="board-members-container" class="space-y-6">
                        <!-- Dinamički renderirani članovi uprave idu ovdje -->
                        <div id="board-list-info" class="p-4 bg-gray-100 rounded-lg text-center text-sm text-gray-500">Učitavanje podataka o Upravi...</div>
                    </div>
                    
                    <button id="add-board-member-btn" class="mt-6 py-2 px-4 rounded-md btn-secondary">+ Dodaj Člana Uprave</button>
                </div>

                <!-- Dokumenti Kluba -->
                <div class="card bg-white p-6 rounded-xl">
                    <h2 class="text-2xl font-bold mb-4" style="color: var(--hkp-red);">Dokumenti Kluba</h2>
                    <div id="document-upload-container" class="space-y-4">
                        <!-- Polje za Statut -->
                        <div class="p-4 border rounded-lg bg-red-50 border-red-200">
                            <label class="block text-sm font-medium text-gray-700 mb-2">Statut Kluba</label>
                            <input type="file" id="doc-statut" class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-red-50 file:text-red-700 hover:file:bg-red-100">
                        </div>
                        <!-- Ostali Dokumenti -->
                        <div class="p-4 border rounded-lg bg-gray-50">
                            <label class="block text-sm font-medium text-gray-700 mb-2">Ostali Dokumenti</label>
                            <input type="file" id="doc-other" multiple class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-gray-100 file:text-gray-700 hover:file:bg-gray-200">
                        </div>
                    </div>
                </div>
            </div>

            <!-- 2. ČLANOVI -->
            <div data-content="members" class="hidden space-y-6">
                <div class="card bg-white p-6 rounded-xl">
                    <h2 class="text-2xl font-bold mb-4" style="color: var(--hkp-red);">Alati za Članove</h2>
                    <div class="flex flex-wrap gap-4 mb-4">
                        <button class="py-2 px-4 rounded-md btn-primary flex items-center gap-2">
                             Upload Excel Članova
                        </button>
                        <button id="download-member-template-btn" class="py-2 px-4 rounded-md btn-secondary flex items-center gap-2">
                             Preuzmi Predložak (.xlsx)
                        </button>
                        <button id="download-all-members-btn" class="py-2 px-4 rounded-md btn-secondary flex items-center gap-2">
                             Preuzmi sve Članove (.xlsx)
                        </button>
                    </div>

                    <h3 class="text-xl font-semibold mt-6 mb-4">Unos Novog Člana</h3>
                    <form id="add-member-form" class="space-y-4">
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <!-- Osnovni Podaci -->
                            <div><label class="block text-sm font-medium text-gray-700">Ime i Prezime</label><input type="text" id="m-name" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">Datum Rođenja</label><input type="date" id="m-birthdate" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">Spol</label><select id="m-gender" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"><option value="M">M (Muški)</option><option value="Ž">Ž (Ženski)</option></select></div>
                            <div><label class="block text-sm font-medium text-gray-700">OIB</label><input type="text" id="m-oib" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">E-mail Sportaša</label><input type="email" id="m-email" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">E-mail Roditelja</label><input type="email" id="m-parent-email" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div class="sm:col-span-2"><label class="block text-sm font-medium text-gray-700">Mjesto Prebivališta</label><input type="text" id="m-residence" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>

                            <!-- Osobni Dokumenti -->
                            <div class="sm:col-span-2"><h4 class="text-lg font-semibold mt-4 mb-2" style="color: var(--hkp-red);">Osobni Dokumenti</h4></div>
                            <div><label class="block text-sm font-medium text-gray-700">Broj Osobne Iskaznice</label><input type="text" id="m-id-num" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">Vrijedi do (O.I.)</label><input type="date" id="m-id-expiry" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">Izdavatelj (O.I.)</label><input type="text" id="m-id-issuer" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">Broj Putovnice</label><input type="text" id="m-pass-num" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">Vrijedi do (Putovnice)</label><input type="date" id="m-pass-expiry" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">Izdavatelj (Putovnice)</label><input type="text" id="m-pass-issuer" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                        </div>

                        <!-- Status i Članarina -->
                        <div class="border-t pt-4 mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div class="flex items-center gap-4 p-3 bg-red-50 rounded-md border border-red-200">
                                <input type="checkbox" id="m-is-active" class="w-5 h-5 text-red-600 rounded">
                                <label for="m-is-active" class="font-medium text-gray-800">Aktivni Natjecatelj/ica</label>
                            </div>
                            <div class="flex items-center gap-4 p-3 bg-amber-50 rounded-md border border-amber-200">
                                <select id="m-group" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border">
                                    <option value="none">-- Odaberi Grupu --</option>
                                    <option value="veteran">Veteran</option>
                                    <option value="u11">Početnici U11</option>
                                    <option value="u13">Mlađi Dječaci U13</option>
                                    <!-- Dinamičke opcije grupe idu ovdje -->
                                </select>
                            </div>

                            <div class="flex items-center gap-4 p-3 bg-green-50 rounded-md border border-green-200">
                                <input type="checkbox" id="m-pays-fee" checked class="w-5 h-5 text-green-600 rounded">
                                <label for="m-pays-fee" class="font-medium text-gray-800">Plaća članarinu</label>
                            </div>
                            <div id="m-fee-amount-div">
                                <label class="block text-sm font-medium text-gray-700">Iznos Članarine (EUR)</label>
                                <input type="number" id="m-fee-amount" value="30" min="0" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border">
                            </div>
                            
                            <div class="sm:col-span-2">
                                <label class="block text-sm font-medium text-gray-700">Slika Člana (Upload)</label>
                                <input type="file" id="m-image-upload" accept="image/*" class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-gray-100 file:text-gray-700 hover:file:bg-gray-200">
                            </div>

                        </div>
                        
                        <button type="submit" class="w-full py-3 px-4 rounded-md btn-primary mt-6">Spremi Novog Člana i Generiraj Dokumente</button>
                        <button type="button" id="generate-docs-btn" class="w-full py-2 px-4 rounded-md btn-secondary hidden">Generiraj Pristupnicu & Privolu</button>
                    </form>
                </div>

                <!-- Lista Članova (s gumbima za akciju) -->
                <div class="card bg-white p-6 rounded-xl">
                    <h2 class="text-2xl font-bold mb-4" style="color: var(--hkp-red);">Popis Svih Članova</h2>
                    <div id="member-list-container" class="space-y-4">
                        <p class="text-gray-500">Učitavanje članova...</p>
                    </div>
                </div>

                <!-- Roditeljski Portal Login Mock -->
                <div id="parent-login-section" class="card bg-white p-6 rounded-xl">
                    <h2 class="text-2xl font-bold mb-4" style="color: var(--hkp-red);">Pristupni Portal (Roditelji/Sportaši)</h2>
                    <p class="text-sm text-gray-500 mb-4">Omogućite roditeljima/sportašima da se prijave e-mailom i OIB-om za upload dokumenata.</p>
                    <form id="parent-login-form" class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <input type="email" id="p-login-email" placeholder="E-mail sportaša ili roditelja" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border" required>
                        <input type="text" id="p-login-oib" placeholder="OIB člana" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border" required>
                        <button type="submit" class="w-full py-3 px-4 rounded-md btn-secondary">Prijavi se</button>
                    </form>
                    <div id="parent-upload-area" class="mt-6 hidden p-4 border border-green-300 bg-green-50 rounded-lg">
                        <h4 class="text-lg font-semibold text-green-700 mb-3">Upload Dokumenta za [Ime Člana]</h4>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div><label class="block text-sm font-medium text-gray-700">Liječnička Potvrda (PDF/JPG)</label><input type="file" id="p-doc-medical" class="w-full text-sm"></div>
                            <div><label class="block text-sm font-medium text-gray-700">Vrijedi do (Liječnički)</label><input type="date" id="p-doc-medical-expiry" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div class="md:col-span-3 grid grid-cols-2 gap-4">
                                <div><label class="block text-sm font-medium text-gray-700">Potpisana Pristupnica</label><input type="file" id="p-doc-pristupnica" class="w-full text-sm"></div>
                                <div><label class="block text-sm font-medium text-gray-700">Potpisana Privola</label><input type="file" id="p-doc-privola" class="w-full text-sm"></div>
                            </div>
                        </div>
                        <button class="mt-4 py-2 px-4 rounded-md btn-primary">Pošalji Dokumente Klubu</button>
                    </div>
                </div>

            </div>

            <!-- 3. TRENERI -->
            <div data-content="coaches" class="hidden space-y-6">
                <div class="card bg-white p-6 rounded-xl">
                    <h2 class="text-2xl font-bold mb-4" style="color: var(--hkp-red);">Unos i Lista Trenera</h2>
                    <form id="add-coach-form" class="space-y-4">
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div><label class="block text-sm font-medium text-gray-700">Ime i Prezime</label><input type="text" id="c-name" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">Datum Rođenja</label><input type="date" id="c-birthdate" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">OIB</label><input type="text" id="c-oib" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">E-mail</label><input type="email" id="c-email" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">IBAN Broj Računa</label><input type="text" id="c-iban" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">Grupa koju Trenira</label><select id="c-group" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"><option value="">-- Odaberi Grupu --</option></select></div>
                            <div class="sm:col-span-2">
                                <label class="block text-sm font-medium text-gray-700">Slika / Ugovor (Upload)</label>
                                <input type="file" id="c-doc-upload" multiple class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-gray-100 file:text-gray-700 hover:file:bg-gray-200">
                            </div>
                        </div>
                        <button type="submit" class="w-full py-3 px-4 rounded-md btn-primary mt-6">Spremi Trenera</button>
                    </form>
                </div>

                <div class="card bg-white p-6 rounded-xl">
                    <h2 class="text-2xl font-bold mb-4" style="color: var(--hkp-red);">Popis Trenera</h2>
                    <div id="coach-list-container" class="space-y-4">
                        <p class="text-gray-500">Učitavanje trenera...</p>
                    </div>
                </div>
            </div>

            <!-- 4. GRUPE i VETERANI -->
            <div data-content="groups" class="hidden space-y-6">
                <div class="card bg-white p-6 rounded-xl">
                    <h2 class="text-2xl font-bold mb-4" style="color: var(--hkp-red);">Upravljanje Grupama i Veteranima</h2>
                    <div class="flex flex-wrap gap-4 mb-4">
                        <button class="py-2 px-4 rounded-md btn-secondary flex items-center gap-2"> Upload Grupa (.xlsx)</button>
                        <button class="py-2 px-4 rounded-md btn-secondary flex items-center gap-2"> Preuzmi Grupe (.xlsx)</button>
                    </div>

                    <h3 class="text-xl font-semibold mt-6 mb-4">Kreiranje Nove Grupe</h3>
                    <form id="add-group-form" class="flex gap-4">
                        <input type="text" id="group-name" placeholder="Naziv Grupe (npr. Kadeti GR)" required class="flex-grow rounded-md border-gray-300 shadow-sm p-3 border">
                        <button type="submit" class="py-3 px-6 rounded-md btn-primary">Dodaj Grupu</button>
                    </form>

                    <h3 class="text-xl font-semibold mt-8 mb-4">Postojeće Grupe</h3>
                    <div id="groups-list-container" class="space-y-4">
                        <p class="text-gray-500">Učitavanje grupa...</p>
                    </div>
                </div>
            </div>

            <!-- 5. PRISUSTVO -->
            <div data-content="attendance" class="hidden space-y-6">
                <div class="card bg-white p-6 rounded-xl">
                    <h2 class="text-2xl font-bold mb-4" style="color: var(--hkp-red);">Evidencija Prisustva Treningu</h2>
                    
                    <h3 class="text-xl font-semibold mt-6 mb-4">Upis Prisustva Trenera i Treninga</h3>
                    <form id="coach-attendance-form" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                        <div><label class="block text-sm font-medium text-gray-700">Datum</label><input type="date" id="att-date" value="${new Date().toISOString().split('T')[0]}" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                        <div><label class="block text-sm font-medium text-gray-700">Trener</label><select id="att-coach" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"><option value="">-- Odaberi --</option></select></div>
                        <div><label class="block text-sm font-medium text-gray-700">Grupa</label><select id="att-group" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"><option value="">-- Odaberi --</option></select></div>
                        <div><label class="block text-sm font-medium text-gray-700">Vrijeme (Od - Do)</label><input type="text" id="att-time" placeholder="18:00 - 19:30" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                        <div class="md:col-span-2"><label class="block text-sm font-medium text-gray-700">Mjesto Treninga</label><select id="att-location" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"><option value="DVORANA SJEVER">DVORANA SJEVER</option><option value="IGRALIŠTE ANG">IGRALIŠTE ANG</option><option value="IGRALIŠTE SREDNJA">IGRALIŠTE SREDNJA</option><option value="Ostalo">Ostalo (Ručni Unos)</option></select></div>
                        <div class="md:col-span-2"><label class="block text-sm font-medium text-gray-700">Statistika</label><p id="coach-att-stats" class="mt-1 p-3 bg-gray-100 rounded-md">Mjesec: 0 treninga / 0 sati</p></div>
                        <button type="submit" class="md:col-span-4 py-3 px-6 rounded-md btn-secondary">Započni Evidenciju Prisustva Sportaša</button>
                    </form>

                    <h3 class="text-xl font-semibold mt-8 mb-4">Evidencija Prisustva Sportaša</h3>
                    <div id="athlete-attendance-list" class="space-y-4">
                        <p class="text-gray-500">Najprije unesite podatke o treningu iznad.</p>
                        <!-- Lista članova iz odabrane grupe za označavanje prisustva -->
                    </div>
                </div>
            </div>

            <!-- 6. NATJECANJA I REZULTATI -->
            <div data-content="competitions" class="hidden space-y-6">
                <div class="card bg-white p-6 rounded-xl">
                    <h2 class="text-2xl font-bold mb-4" style="color: var(--hkp-red);">Unos Novog Natjecanja i Rezultata</h2>
                    <form id="add-competition-form" class="space-y-4">
                        
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <!-- Tip Natjecanja -->
                            <div class="md:col-span-3">
                                <label class="block text-sm font-medium text-gray-700">Tip Natjecanja</label>
                                <select id="comp-type" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border">
                                    <option>PRVENSTVO HRVATSKE</option>
                                    <option>MEĐUNARODNI TURNIR</option>
                                    <option>REPREZENTATIVNI NASTUP</option>
                                    <option>HRVAČKA LIGA ZA SENIORE</option>
                                    <option>MEĐUNARODNA HRVAČKA LIGA ZA KADETE</option>
                                    <option>REGIONALNO PRVENSTVO</option>
                                    <option>LIGA ZA DJEVOJČICE</option>
                                    <option>OSTALO</option>
                                </select>
                            </div>
                            <!-- Reprezentativni Nastup Opcije -->
                            <div id="rep-options" class="md:col-span-3 hidden border p-4 rounded-md bg-gray-50">
                                <label class="block text-sm font-medium text-gray-700 mb-2">Opcije Reprezentativnog Nastupa</label>
                                <select id="rep-sub-type" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border">
                                    <option>PRVENSTVO EUROPE</option><option>PRVENSTVO SVIJETA</option><option>PRVENSTVO BALKANA</option><option>UWW TURNIR</option>
                                </select>
                            </div>

                            <!-- Ostalo / Ime Natjecanja -->
                            <div class="md:col-span-2">
                                <label class="block text-sm font-medium text-gray-700">Ime Natjecanja / Detalji "Ostalo"</label>
                                <input type="text" id="comp-name-details" placeholder="Npr. Grand Prix Zagreb Open" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border">
                            </div>
                            
                            <!-- Datum i Mjesto -->
                            <div><label class="block text-sm font-medium text-gray-700">Datum OD</label><input type="date" id="comp-date-from" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">Datum DO (opcionalno)</label><input type="date" id="comp-date-to" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">Mjesto Natjecanja</label><input type="text" id="comp-venue" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">Država (Kratica)</label><input type="text" id="comp-country-code" placeholder="Npr. CRO" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>

                            <!-- Stil, Uzrast i Mjere -->
                            <div><label class="block text-sm font-medium text-gray-700">Stil Hrvanja</label><select id="comp-style" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"><option>GR</option><option>FS</option><option>WW</option><option>BW</option><option>MODIFICIRANO</option></select></div>
                            <div><label class="block text-sm font-medium text-gray-700">Uzrast</label><select id="comp-age-group" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"><option>POČETNICI</option><option>U11</option><option>U13</option><option>U15</option><option>U17</option><option>U20</option><option>U23</option><option>SENIORI</option></select></div>
                            
                            <!-- Ekipni Podaci -->
                            <div><label class="block text-sm font-medium text-gray-700">Ekipni Poredak (HKP)</label><input type="number" id="comp-team-rank" placeholder="Mjesto (npr. 1)" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">Br. Natjecatelja (HKP)</label><input type="number" id="comp-hkp-count" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">Ukupan Br. Natjecatelja</label><input type="number" id="comp-total-athletes" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">Br. Klubova / Zemalja</label><input type="text" id="comp-clubs-countries" placeholder="npr. 50 klubova / 10 zemalja" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                        </div>

                        <div class="border-t pt-4">
                            <label class="block text-sm font-medium text-gray-700">Trener(i) koji je vodio</label>
                            <input type="text" id="comp-coach-led" placeholder="Ime Prezime (+ Ime Prezime)" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border">
                        </div>

                        <div class="border p-4 rounded-md bg-red-50 border-red-200">
                            <label class="block text-sm font-medium text-gray-700">Zapažanje Trenera / Podaci za Objavu</label>
                            <textarea id="comp-observation" rows="3" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></textarea>
                        </div>
                        
                        <h3 class="text-xl font-semibold mt-6 mb-4">Rezultati Hrvača (<span id="comp-athlete-count">0</span> sportaša)</h3>
                        <div id="athlete-results-container" class="space-y-4 border p-4 rounded-md">
                            <p class="text-gray-500">Unesite broj natjecatelja HKP-a iznad.</p>
                            <!-- Dinamička polja za rezultate sportaša idu ovdje -->
                        </div>

                        <div class="flex flex-wrap gap-4 mt-4">
                            <button type="button" class="py-2 px-4 rounded-md btn-secondary flex items-center gap-2"> Upload Rezultata (.xlsx)</button>
                            <button type="button" class="py-2 px-4 rounded-md btn-secondary flex items-center gap-2"> Predložak Tablice</button>
                        </div>

                        <div class="border-t pt-4 space-y-4">
                            <label class="block text-sm font-medium text-gray-700">Upload Slika s Natjecanja / Biltena</label>
                            <input type="file" multiple class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-gray-100 file:text-gray-700 hover:file:bg-gray-200">
                            <input type="url" placeholder="Link na objavu kluba na web stranici" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border">
                        </div>

                        <button type="submit" class="w-full py-3 px-4 rounded-md btn-primary mt-6">Spremi Natjecanje i Rezultate</button>
                    </form>
                </div>
            </div>

            <!-- 7. STATISTIKA -->
            <div data-content="statistics" class="hidden space-y-6">
                <div class="card bg-white p-6 rounded-xl">
                    <h2 class="text-2xl font-bold mb-4" style="color: var(--hkp-red);">Statistika i Izvještaji</h2>
                    <p class="text-sm text-gray-500 mb-4">Filtrirajte podatke o rezultatima, prisustvu i članarinama.</p>

                    <form class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                        <div><label class="block text-sm font-medium text-gray-700">Godina</label><select class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"><option>2025</option><option>2024</option></select></div>
                        <div><label class="block text-sm font-medium text-gray-700">Mjesec</label><select class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"><option>Sve</option><option>Siječanj</option></select></div>
                        <div><label class="block text-sm font-medium text-gray-700">Sportaš</label><select class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"><option>Svi</option></select></div>
                        <div><label class="block text-sm font-medium text-gray-700">Tip Natjecanja</label><select class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"><option>Sve</option><option>PH</option></select></div>
                        <div class="md:col-span-4 flex justify-end">
                            <button type="submit" class="py-2 px-4 rounded-md btn-primary">Generiraj Izvještaj</button>
                        </div>
                    </form>

                    <div id="statistics-results" class="p-4 border-t pt-4">
                        <h3 class="text-xl font-semibold mb-3">Statistika za 2025. godinu</h3>
                        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
                            <div class="bg-red-50 p-4 rounded-lg"><p class="text-sm text-gray-500">Ukupno Natjecanja</p><p class="text-2xl font-bold text-red-700">15</p></div>
                            <div class="bg-amber-50 p-4 rounded-lg"><p class="text-sm text-gray-500">Ukupno Pobjeda</p><p class="text-2xl font-bold text-amber-600">150</p></div>
                            <div class="bg-gray-100 p-4 rounded-lg"><p class="text-sm text-gray-500">Aktivnih Članova</p><p class="text-2xl font-bold text-gray-800">75</p></div>
                            <div class="bg-green-50 p-4 rounded-lg"><p class="text-sm text-gray-500">Plaćenih Članarina (%)</p><p class="text-2xl font-bold text-green-700">92%</p></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 8. ČLANARINE -->
            <div data-content="fees" class="hidden space-y-6">
                <div class="card bg-white p-6 rounded-xl">
                    <h2 class="text-2xl font-bold mb-4" style="color: var(--hkp-red);">Evidencija i Kreiranje Članarina</h2>
                    
                    <form id="create-fees-form" class="space-y-4 border-b pb-6 mb-6">
                        <h3 class="text-xl font-semibold mt-4 mb-2">Kreiranje Novih Uplatnica</h3>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div><label class="block text-sm font-medium text-gray-700">Za Mjesec</label><select id="fee-month" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"><option>Siječanj</option><option>Veljača</option></select></div>
                            <div><label class="block text-sm font-medium text-gray-700">Za Godinu</label><input type="number" id="fee-year" value="${new Date().getFullYear()}" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></div>
                            <div><label class="block text-sm font-medium text-gray-700">Kome Kreirati</label><select id="fee-target" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"><option value="all">SVI koji plaćaju</option><option value="individual">Pojedinačno</option></select></div>
                        </div>
                        <div id="fee-individual-select" class="hidden">
                            <label class="block text-sm font-medium text-gray-700">Odaberite Člana</label>
                            <select class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"><option>-- Pretraži članove --</option></select>
                        </div>
                        <div class="flex justify-between items-center">
                            <button type="submit" class="py-3 px-6 rounded-md btn-primary">Kreiraj Članarine</button>
                            <button type="button" id="send-fee-emails-btn" class="py-2 px-4 rounded-md btn-secondary">Pošalji E-mail obavijest Roditeljima</button>
                        </div>
                    </form>

                    <h3 class="text-xl font-semibold mt-4 mb-4">Evidencija Plaćenih/Neplaćenih Članarina</h3>
                    <div id="fees-list-container" class="space-y-4">
                        <p class="text-gray-500">Nema kreiranih članarina.</p>
                        <!-- Dinamička lista članarina -->
                    </div>
                </div>
            </div>

            <!-- 9. KOMUNIKACIJA -->
            <div data-content="comms" class="hidden space-y-6">
                <div class="card bg-white p-6 rounded-xl">
                    <h2 class="text-2xl font-bold mb-4" style="color: var(--hkp-red);">Slanje Obavijesti i Poruka</h2>
                    <p class="text-sm text-gray-500 mb-4">Pošaljite E-mail ili WhatsApp poruke odabranim članovima.</p>

                    <h3 class="text-xl font-semibold mt-4 mb-2">Odabir Primatelja</h3>
                    <div class="flex flex-wrap gap-4 mb-4">
                        <button class="py-2 px-4 rounded-md btn-secondary">Svi Članovi</button>
                        <button class="py-2 px-4 rounded-md btn-secondary">Aktivni Natjecatelji</button>
                        <button class="py-2 px-4 rounded-md btn-secondary">Veterani</button>
                        <button class="py-2 px-4 rounded-md btn-secondary">Neplatiše Članarine</button>
                    </div>
                    
                    <form id="communication-form" class="space-y-4">
                        <label class="block text-sm font-medium text-gray-700">Odabrani E-mailovi (Sportaši/Roditelji)</label>
                        <textarea id="comms-emails" rows="3" placeholder="email1@domena.hr; email2@domena.hr;..." class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-3 border"></textarea>

                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <button type="submit" class="py-3 px-4 rounded-md btn-primary">Pošalji E-mail</button>
                            <button type="button" class="py-3 px-4 rounded-md btn-secondary">Generiraj WhatsApp Link (Grupe)</button>
                        </div>
                        <button type="button" class="w-full py-2 px-4 rounded-md btn-secondary"> Preuzmi E-mail Liste (.xlsx)</button>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <!-- Firebase i Glavna JS Logika -->
    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
        import { getAuth, signInAnonymously, signInWithCustomToken } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
        import { 
            getFirestore, 
            collection, 
            addDoc, 
            onSnapshot, 
            query, 
            serverTimestamp 
        } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

        let db;
        let auth;
        let userId = 'anoniman'; 
        let membersData = []; // Cache za članove
        let groupsData = []; // Cache za grupe
        
        const CLUB_IBAN = "HR6923860021100518154";
        const CLUB_OIB = "60911784858";
        const CLUB_ADDRESS = "Miklinovec 6a, 48000 Koprivnica";

        // --- PDF GENERATOR (MOCK) ---
        const { jsPDF } = window.jspdf;

        function generateAndDownloadPDF(type, member) {
            const doc = new jsPDF('p', 'mm', 'a4');
            const margin = 15;
            let y = margin;
            const lineHeight = 7;
            const maxWidth = 180;

            const header = `HRVAČKI KLUB "PODRAVKA"\n48000 Koprivnica, Miklinovec 6a\nmob:091/456-23-21, web: www.hk-podravka.hr, e-mail: hsk-podravka@gmail.com`;

            // Stilovi
            doc.setFont('Helvetica', 'bold');
            doc.setFontSize(10);
            doc.setTextColor('#b91c1c');
            doc.text(header, doc.internal.pageSize.getWidth() / 2, y, { align: 'center' });
            y += lineHeight * 4;

            doc.setTextColor(0, 0, 0);
            doc.setFont('Helvetica', 'normal');
            doc.setFontSize(12);

            // Zaglavlje Člana
            doc.text(`Ime i Prezime: ${member.name}`, margin, y);
            y += lineHeight;
            doc.text(`Datum Rođenja: ${member.birthDate}`, margin, y);
            y += lineHeight;
            doc.text(`OIB: ${member.oib}`, margin, y);
            y += lineHeight * 2;
            
            // Naslov dokumenta
            doc.setFont('Helvetica', 'bold');
            doc.setFontSize(16);
            doc.text(type === 'pristupnica' ? 'PRISTUPNICA KLUBU' : 'PRIVOLA ZA OBRADU OSOBNIH PODATAKA', doc.internal.pageSize.getWidth() / 2, y, { align: 'center' });
            y += lineHeight * 2;
            doc.setFont('Helvetica', 'normal');
            doc.setFontSize(10);
            
            let content;
            if (type === 'pristupnica') {
                content = `
                    OIB Kluba: ${CLUB_OIB}, Žiro-račun: ${CLUB_IBAN}, Podravska banka d.d. Koprivnica

                    STATUT KLUBA - ČLANSTVO
                    Članak 14.
                    Članom Kluba može postati svaki poslovno sposoban državljanin Republike Hrvatske i pravna osoba sa sjedištem u Republici Hrvatskoj, koji prihvaćaju načela na kojima se Klub zasniva i Statut Kluba. Članom kluba mogu postati i fizičke osobe bez poslovne sposobnosti za koje pristupnicu ispunjava roditelj (staratelj). Osobe bez poslovne sposobnosti mogu sudjelovati u radu Kluba bez prava odlučivanja.
                    Članak 15.
                    Članom Kluba se postaje potpisivanjem pristupnice i izjavom o prihvaćanju Statuta te upisom u Registar članova koji vodi tajnik Kluba, a odluku o primitku u članstvo donosi Predsjedništvo. NAPOMENA: Cijeli Statut dostupan je na www.hk-podravka.hr/o-klubu

                    STATUT KLUBA – PRESTANAK ČLANSTVA
                    Članak 21.
                    Članstvo u klubu prestaje:
                    - dragovoljnim istupom – ispisivanjem uz pismenu izjavu (istupnica), a kada se radi o aktivnom natjecatelju, uz suglasnost Predsjedništva kluba sukladno važećim športskim pravilnicima Hrvatskog hrvačkog saveza
                    - neplaćanjem članarine duže od šest mjeseci,
                    - isključenjem po odluci Stegovne komisije Kluba (ukoliko je formirana) uz pravo žalbe Skupštini,
                    - gubitkom građanskih prava.
                    Isključeni član ima pravo prigovora Skupštini čija je odluka o isključenju konačna. NAPOMENA: Istupnica je dostupna je www.hk-podravka.hr/o-klubu

                    ČLANARINA JE OBVEZUJUĆA TIJEKOM CIJELE GODINE (12 MJESECI) I ČLAN JU JE DUŽAN PLAČATI SVE DOK DRAGOVOLJNO NE ISTUPI IZ KLUBA ODNOSNO NE DOSTAVI ISPUNJENU ISTUPNICU O PRESTANKU ČLANSTVA.

                    IZJAVA O ODGOVORNOSTI
                    Hrvanje je borilački šport u kojemu su kao i ostalim drugim sportovima moguće ozljede prilikom treninga i natjecanja. Svojim potpisom suglasni smo da naše dijete pohađa treninge i da se kao član hrvačkog kluba Podravka natječe prema predviđenom klupskom kalendaru te da ga se fotografira isključivo u svrhu stručnih radova i informiranja. Za eventualne nastale povrede prilikom treninga ili natjecanja u potpunosti preuzimamo odgovornost. Također obvezujemo se kao roditelji-staratelji da ćemo u roku od šest mjeseci od dana upisa svojem djetetu omogućiti adekvatnu opremu za trening i natjecanje (hrvačke patike i hrvački dresovi). Isto tako svojim potpisom prihvačam/o načela na kojima se klub zasniva i Statut Kluba.
                    
                    POTPIS ČLANA:___________________________________________
                    POTPIS RODITELJA/STARATELJA:____________________________ (za punoljetnog člana ovaj potpis je nepotreban)
                `;
            } else { // Privola
                content = `
                    Sukladno Zakonu o zaštiti osobnih podataka, uređuje se zaštita osobnih podataka o fizičkim osobama te nadzor nad prikupljanjem, obradom i korištenjem osobnih podataka u Republici Hrvatskoj. Ovim Zakonom osigurava se provedba Opće uredbe o zaštiti podataka. Svrha zaštite osobnih podataka je zaštita privatnog života i ostalih ljudskih prava i temeljnih sloboda.

                    PRIVOLA
                    Ovime dajem privolu da se moji osobni podaci (ime i prezime, OIB, datum rođenja, adresa stanovanja, fotografija, video snimka, broj telefona/mobitela, e-mail adresa, broj putovnice/osobne iskaznice, potvrda o zdravstvenoj sposobnosti, specifična medicinska stanja, ime škole/fakulteta) koriste u svrhu vođenja i redovnog funkcioniranja Kluba, prijave i sudjelovanja na relevantnim natjecanjima u RH i izvan nje te objavljivanja na službenim stranicama Kluba, društvenim mrežama Kluba, Hrvatskog hrvačkog saveza, Hrvatskog olimpijskog odbora i ostalih gradskih i državnih institucija vezanih uz sport.
                    Navedeni podaci će se koristiti samo u navedene svrhe i Klub ih neće dostavljati trećima. Upoznat sam s pravom da zatražim pristup, ispravak, brisanje podataka, ograničavanje obrade, s pravom na ulaganje prigovora, pravom na prenosivost podataka, pravom na podnošenje prigovora Agenciji za zaštitu osobnih podataka, te postavljanjem upita na email adresu kluba ako smatram da je došlo do bilo kakve povrede u obradi osobnih podataka. Ova privola vrijedi do opoziva i može se povući bilo kada na jednostavan način.

                    Ova privola stupa na snagu danom potpisa.
                    
                    U _____________________________ ; _____________________ g.
                    Član kluba: ${member.name}
                    Potpis : ____________________
                    Roditelj/staratelj malodobnog člana kluba: __________________________________
                    Potpis roditelja/staratelja : ____________________
                `;
            }

            const splitContent = doc.splitTextToSize(content.trim(), maxWidth);
            doc.text(splitContent, margin, y);

            doc.save(`${member.name.replace(/\s/g, '_')}_${type}.pdf`);
        }

        // --- FUNKCIJE ZA RENDERIRANJE I LOGIKU ---

        function renderMembers(members) {
            membersData = members; // Ažuriranje cachea
            const container = document.getElementById('member-list-container');
            if (!container) return;

            if (members.length === 0) {
                container.innerHTML = '<p class="text-gray-500">Nema unesenih članova.</p>';
                return;
            }

            container.innerHTML = members.map(member => {
                const age = new Date().getFullYear() - new Date(member.birthDate).getFullYear();
                const isActive = member.isActive ? 'Aktivni' : 'Neaktivni';
                const isRed = member.medicalExpiry && (new Date(member.medicalExpiry) < new Date(Date.now() + 14 * 24 * 60 * 60 * 1000));
                
                return `
                    <div class="p-4 bg-gray-50 border border-red-200 rounded-lg flex flex-col sm:flex-row justify-between items-center transition duration-150 hover:bg-red-50 ${isRed ? 'ring-2 ring-red-500' : ''}">
                        <div class="mb-2 sm:mb-0 w-full sm:w-1/3">
                            <p class="font-semibold text-gray-900">${member.name} (${age} god., ${member.gender})</p>
                            <p class="text-sm text-gray-600">OIB: ${member.oib} | Grupa: <span class="text-red-600">${member.group}</span></p>
                        </div>
                        <div class="flex flex-col sm:flex-row gap-2 w-full sm:w-2/3 justify-end items-center">
                            <span class="text-xs font-medium px-2 py-1 rounded-full ${member.paysFee ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}">${member.paysFee ? 'PLAĆA ČLAN.' : 'NE PLAĆA ČLAN.'}</span>
                            <span class="text-xs text-gray-400">Liječnički: ${member.medicalExpiry ? new Date(member.medicalExpiry).toLocaleDateString('hr-HR') : 'NEMA'}</span>
                            <div class="flex gap-2">
                                <button data-member-id="${member.id}" class="py-1 px-3 text-xs rounded btn-primary edit-member-btn">Promijeni</button>
                                <button data-member-email="${member.email}" class="py-1 px-3 text-xs rounded btn-secondary email-member-btn">E-mail</button>
                                <button data-member-id="${member.id}" class="py-1 px-3 text-xs rounded bg-gray-300 delete-member-btn">Obriši</button>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
            
            // Postavljanje listenera na novo generirane gumbe
            document.querySelectorAll('.edit-member-btn').forEach(button => {
                button.addEventListener('click', (e) => console.log(`Edit member ${e.target.dataset.memberId}`));
            });
            document.querySelectorAll('.email-member-btn').forEach(button => {
                button.addEventListener('click', (e) => {
                    const emailsField = document.getElementById('comms-emails');
                    emailsField.value = `${emailsField.value.trim()}${emailsField.value.trim() ? '; ' : ''}${e.target.dataset.memberEmail}`;
                    switchSection('comms');
                });
            });
            document.querySelectorAll('.delete-member-btn').forEach(button => {
                button.addEventListener('click', (e) => {
                    if (confirm('Jeste li sigurni da želite obrisati člana? (Mock)')) {
                        console.log(`Delete member ${e.target.dataset.memberId}`);
                    }
                });
            });
        }

        async function addMember(e) {
            e.preventDefault();
            const form = e.target;
            const member = {
                name: form.querySelector('#m-name').value.trim(),
                birthDate: form.querySelector('#m-birthdate').value,
                gender: form.querySelector('#m-gender').value,
                oib: form.querySelector('#m-oib').value.trim(),
                email: form.querySelector('#m-email').value.trim(),
                parentEmail: form.querySelector('#m-parent-email').value.trim(),
                residence: form.querySelector('#m-residence').value.trim(),
                idNum: form.querySelector('#m-id-num').value.trim(),
                idExpiry: form.querySelector('#m-id-expiry').value,
                idIssuer: form.querySelector('#m-id-issuer').value.trim(),
                passNum: form.querySelector('#m-pass-num').value.trim(),
                passExpiry: form.querySelector('#m-pass-expiry').value,
                passIssuer: form.querySelector('#m-pass-issuer').value.trim(),
                isActive: form.querySelector('#m-is-active').checked,
                paysFee: form.querySelector('#m-pays-fee').checked,
                feeAmount: parseFloat(form.querySelector('#m-fee-amount').value) || 0,
                group: form.querySelector('#m-group').value,
                medicalExpiry: null, // Dodaje se preko portala/ažuriranja
                accessDate: new Date().toISOString().split('T')[0], // Datum davanja privole/pristupa
                userId: userId, 
                createdAt: serverTimestamp()
            };

            if (!member.name || !member.oib) {
                alert('Ime i OIB su obvezni.'); return;
            }

            try {
                const membersCollectionRef = collection(db, 'artifacts', appId, 'public', 'data', 'members');
                await addDoc(membersCollectionRef, member);
                
                // Generiranje Pristupnice i Privole (PDF download)
                generateAndDownloadPDF('pristupnica', member);
                generateAndDownloadPDF('privola', member);

                alert(`Član ${member.name} uspješno dodan. Pristupnica i Privola generirane za preuzimanje.`);
                form.reset();
                form.querySelector('#m-fee-amount').value = 30;

            } catch (error) {
                console.error("Greška pri dodavanju člana:", error);
            }
        }
        
        function renderGroups(groups) {
            groupsData = groups;
            const container = document.getElementById('groups-list-container');
            const select = document.getElementById('m-group');
            
            if (!container || !select) return;

            // Renderiranje liste
            if (groups.length === 0) {
                container.innerHTML = '<p class="text-gray-500">Nema unesenih grupa.</p>';
            } else {
                container.innerHTML = groups.map(group => `
                    <div class="p-4 bg-gray-50 border border-amber-200 rounded-lg flex justify-between items-center hover:bg-amber-50">
                        <p class="font-semibold text-gray-900">${group.name}</p>
                        <button data-group-id="${group.id}" class="py-1 px-3 text-xs rounded bg-red-500 text-white delete-group-btn">Obriši</button>
                    </div>
                `).join('');
            }

            // Ažuriranje select polja
            select.innerHTML = `<option value="none">-- Odaberi Grupu --</option>`;
            select.innerHTML += groups.map(group => `<option value="${group.name}">${group.name}</option>`).join('');
            
            document.querySelectorAll('.delete-group-btn').forEach(button => {
                button.addEventListener('click', (e) => console.log(`Delete group ${e.target.dataset.groupId}`));
            });
        }
        
        async function addGroup(e) {
            e.preventDefault();
            const groupNameInput = document.getElementById('group-name');
            const name = groupNameInput.value.trim();

            if (!name) return;

            try {
                const groupsCollectionRef = collection(db, 'artifacts', appId, 'public', 'data', 'groups');
                await addDoc(groupsCollectionRef, { name: name, userId: userId, createdAt: serverTimestamp() });
                groupNameInput.value = '';
            } catch (error) {
                console.error("Greška pri dodavanju grupe:", error);
            }
        }

        // --- NAVIGACIJA ---

        function switchSection(target) {
            document.querySelectorAll('#app-tabs button').forEach(button => {
                if (button.dataset.section === target) {
                    button.classList.add('tab-active');
                    button.classList.remove('text-gray-500', 'hover:text-gray-700');
                } else {
                    button.classList.remove('tab-active');
                    button.classList.add('text-gray-500', 'hover:text-gray-700');
                }
            });

            document.querySelectorAll('#sections-container > div').forEach(section => {
                if (section.dataset.content === target) {
                    section.classList.remove('hidden');
                } else {
                    section.classList.add('hidden');
                }
            });
        }

        function setupTabs() {
            document.querySelectorAll('#app-tabs button').forEach(button => {
                button.addEventListener('click', () => switchSection(button.dataset.section));
            });
            switchSection('klub'); 
        }

        // --- INICIJALIZACIJA ---

        async function initApp() {
            if (!firebaseConfig) {
                console.error("Firebase konfiguracija nije dostupna.");
                return;
            }

            const app = initializeApp(firebaseConfig);
            db = getFirestore(app);
            auth = getAuth(app);
            
            try {
                if (initialAuthToken) {
                    await signInWithCustomToken(auth, initialAuthToken);
                } else {
                    await signInAnonymously(auth);
                }
                
                userId = auth.currentUser?.uid || crypto.randomUUID();
                document.getElementById('user-id-display').textContent = userId;

                console.log("Autentifikacija uspješna. Korisnik:", userId);
                
                // 1. Postavljanje Firestore listenera za ČLANOVE
                const membersCollectionRef = collection(db, 'artifacts', appId, 'public', 'data', 'members');
                onSnapshot(query(membersCollectionRef), (snapshot) => {
                    const members = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data(), createdAt: doc.data().createdAt?.toDate().toISOString() }));
                    renderMembers(members);
                }, (error) => {
                    console.error("Greška pri slušanju promjena u kolekciji članova:", error);
                });
                
                // 2. Postavljanje Firestore listenera za GRUPE
                const groupsCollectionRef = collection(db, 'artifacts', appId, 'public', 'data', 'groups');
                onSnapshot(query(groupsCollectionRef), (snapshot) => {
                    const groups = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
                    renderGroups(groups);
                }, (error) => {
                    console.error("Greška pri slušanju promjena u kolekciji grupa:", error);
                });

                // --- Postavljanje Listenera za Forme ---
                document.getElementById('add-member-form')?.addEventListener('submit', addMember);
                document.getElementById('add-group-form')?.addEventListener('submit', addGroup);
                
                // --- Inicijalizacija Navigacije ---
                setupTabs();

            } catch (error) {
                console.error("Greška pri autentifikaciji:", error);
            }
        }

        window.onload = initApp;
    </script>
</body>
</html>
