# Tdlib Python

**Tdlib Python** {description}

- 🇮🇩 [Indonesia](https://github.com/zerounintezaragler/tdlib_python/blob/main/README.md)
- 🇨🇿 [Afrika](https://github.com/zerounintezaragler/tdlib_python/blob/main/README_AFRIKA.md)
- 🇨🇳 [China](https://github.com/zerounintezaragler/tdlib_python/blob/main/README_CHINA.md)
- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 [English](https://github.com/zerounintezaragler/tdlib_python/blob/main/README_ENGLISH.md)
- 🇮🇳 [India](https://github.com/zerounintezaragler/tdlib_python/blob/main/README_INDIA.md)
- 🇮🇩 [Jawa](https://github.com/zerounintezaragler/tdlib_python/blob/main/README_JAWA.md)
- 🇯🇵 [Jepang](https://github.com/zerounintezaragler/tdlib_python/blob/main/README_JEPANG.md)
- 🇰🇷 [Korea](https://github.com/zerounintezaragler/tdlib_python/blob/main/README_KOREA.md)
- 🇷🇺 [Russia](https://github.com/zerounintezaragler/tdlib_python/blob/main/README_RUSSIA.md)
- 🇮🇩 [Sunda](https://github.com/zerounintezaragler/tdlib_python/blob/main/README_SUNDA.md)
- 🇹🇭 [Thailand](https://github.com/zerounintezaragler/tdlib_python/blob/main/README_THAILAND.md)

## Fakta

- Library ini tidak terikat banyak depenencides pihak 3

## Feature

- [x] **Sangat Cepat** Library Async (**Tidak Memblokir Threads**)
- [x] **Mudah Digunakan**

## Contoh

- [Contoh Sederhana](https://github.com/zerounintezaragler/tdlib_python/tree/main/quickstart)



## Memasang

sebelum memasang pastikan kamu mengetahui basic python setidaknya kamu sudah menginstall ptyhon dalam komputer / device kamu. [Python Website](https://www.python.org)

- **Python**

  ```bash
  pip install tdlib-python
  ```

## Dokumentasi

### EnsureInitialized

method wajib di panggil bebas mau setelah **on** / sebelum method **on** tapi saya sarankan sebelum **on**

**contoh:**

```dart
  tdlibPythonZerounIntezarAgler.ensureInitialized(libraryPath="fork/dependencies/lib/libtdlib_python.so")
```

### Initialized

method ini wajib di panggil setelah method **on** karena untuk mengolah update

**contoh:**

```dart
  await tdlibPythonZerounIntezarAgler.initialized()
```

### On

method on ini berguna untuk mendapatkan update data dari invoke / update

**contoh:**

```dart

  def on_callback(update:dict):
    print(update)

  tdlibPythonZerounIntezarAgler.on(event_name="update", on_callback=on_callback)
  
```


### createClient

untuk membuat client baru pastikan kamu memanggil method.

**contoh:**

```dart
newClientId = tdlibPythonZerounIntezarAgler.createClient()
print(newClientId)
```


### Invoke

untuk memanggil api kamu perlu membaca dokumentasi langsung

- [Url Docs](other_url_docs) mudah di baca untuk umum 

disini saya hanya menyediakan parameters data map, map / json ini terdapat beberapa key penting


| Key            | Description                                                                                                    | Value      | Wajib Diisi                                              |
|----------------|----------------------------------------------------------------------------------------------------------------|------------|----------------------------------------------------------|
| **@type**      | ini isi dengan method dari                                                                              | **String** | **ya**                                                   |
| **@client_id** | ini berisi client id dari method **createClient**                                                              | **int**    | **jika untuk method sync ada yang wajib ada yang tidak** |
| **@extra**     | isi dengan unique id karena method async tidak return data langsung jadi perlu extra sebagai kunci return data | **String** | **Tidak**                                                |


jika sudah mengisi parameters wajib, kita lanjut bagaimana menginvoke api

- **SetLogVerbosityLevel**
  di karenakan ini method log maka kamu menggunakan method sync 
  dan tidak wajib mengisi key **@client_id**

  contoh: 


```dart
  tdlibPythonZerounIntezarAgler.invokeSync(parameters={
    "@type": "setLogVerbosityLevel",
    "new_verbosity_level": 0,
  });
```

- **SendMessage**
  untuk mengirim pesan menggunakan library ini pastikan client sudah login
  [Referensi Dokumentasi SendMessage](url docs)

```dart

        /// ambil from createClient atau pembaruan
        client_id = 1;
        getMe = await tdlibPythonZerounIntezarAgler.invoke(parameters={
          "@type": "getMe",
          "@client_id": client_id,
        });
        print(getMe);
        await tdlibPythonZerounIntezarAgler.invoke(parameters={
          "@type": "sendMessage",
          "@client_id": client_id,
          "chat_id": getMe["id"],
          "type": "text",
          "text": "Hello",
        });
```

di atas itu hanyalah contoh, untuk menggunakan method lain isi saja data parameters, pastikan parameters key wajib di isi sesuai table, maksud saya ada beberapa key yang wajib di isi, jika tidak ya akan mengirim data error



## Bantuan

**Sulit**? saya sudah membangun **library** ini **sebaik** mungkin dan **berusaha mudah** di baca dan **digunakan sebaik mungkin**. 

jika **kamu** masih **merasa** **kesulitan** dan **kebingungan** **cobalah bergabung** ke **group** kami secara **gratis tanpa biaya apapun**

- [Telegram](https://t.me/DEVELOPER_GLOBAL_PUBLIC)


**sebelum join** pastikan **memakai profile** yang **jelas** kami tidak keberatan kamu siapa, dan pangkat apapun, tapi **pastikan** **ada username dan photo profile**, dan usahakan untuk **chat di group** **tidak chat pribadi** karena itu **group umum dan mungkin orang lain kebingungan**. jika **tidak mengikuti** ini kemungkinan **tidak bisa akses chat di group dan bakal di banned**, solusi pakai akun kedua, karena setelah di banned kami tidak bisa merespond cepat


## Support Me

Jika kamu merasa program ini berguna, kamu bisa support saya [GITHUB zerounintezaragler](https://github.com/zerounintezaragler) di link itu tersedia social media dan sponsor saya. saya tidak keberatan jika kamu hanya follow / donasi uang sedikit

![]({gopay_qr_url})

- https://github.com/sponsors/zerounintezaragler
- https://www.patreon.com/c/{patreon_username}
- https://opencollective.com/{opencollective_username}
- https://paypal.me/{paypal_username}

Terimakasih


zerounintezaragler - 18-07-2025


## Tags

- tdlib_python python

