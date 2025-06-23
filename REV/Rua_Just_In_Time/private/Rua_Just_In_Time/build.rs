use std::{env, fs, path::Path};

use chacha20::{cipher::{KeyIvInit, StreamCipher}, XChaCha20};
use lzma_rs::lzma_compress;
use mlua::Lua;
use rand::RngCore;

fn encode_byte(mut b: u8) -> u8 {
    b = b.wrapping_add(4);
    b ^= 0x17;
    b.rotate_right(1)
}

fn main() {
    let out_dir  = env::var("OUT_DIR").unwrap();
    let lua_src  = fs::read_to_string("scripts/script.lua").unwrap();
    let blob_out = Path::new(&out_dir).join("script.enc");

    let lua      = Lua::new();
    let dumped   = lua.load(&lua_src).into_function()
                     .unwrap().dump(true);
    let mut comp = Vec::new();
    lzma_compress(&mut dumped.as_slice(), &mut comp).unwrap();

    let mut key = [0u8; 32];
    let mut iv  = [0u8; 24];
    rand::rngs::OsRng.fill_bytes(&mut key);
    rand::rngs::OsRng.fill_bytes(&mut iv);

    let mut cipher = XChaCha20::new(&key.into(), &iv.into());
    cipher.apply_keystream(&mut comp);

    const FLAG: &str =
        "kctf-jr{2ba0fc74c0db3117617f5343f7269ce7612324b541c881f53ac2693812c1884b}";
    let enc_flag: Vec<u8> = FLAG.bytes().map(encode_byte).collect();

    // [ key | iv | clen | cipher | elen | encoded ]
    let mut blob = Vec::with_capacity(32+24+4+comp.len()+4+enc_flag.len());
    blob.extend_from_slice(&key);
    blob.extend_from_slice(&iv);
    blob.extend_from_slice(&(comp.len() as u32).to_le_bytes());
    blob.extend_from_slice(&comp);
    blob.extend_from_slice(&(enc_flag.len() as u32).to_le_bytes());
    blob.extend_from_slice(&enc_flag);

    fs::write(blob_out, &blob).unwrap();
    println!("cargo:rerun-if-changed=scripts/script.lua");
}