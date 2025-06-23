use chacha20::{cipher::{KeyIvInit, StreamCipher}, XChaCha20};
use mlua::{Lua, Function, String as LuaStr};
use std::convert::TryInto;

static BLOB: &[u8] = include_bytes!(concat!(env!("OUT_DIR"), "/script.enc"));

fn decrypt() -> (Vec<u8>, Vec<u8>) {
    let (key, rest) = BLOB.split_at(32);
    let (iv,  rest) = rest.split_at(24);

    let (clen_b, rest) = rest.split_at(4);
    let clen = u32::from_le_bytes(clen_b.try_into().unwrap()) as usize;
    let (cipher, rest) = rest.split_at(clen);

    let (elen_b, rest) = rest.split_at(4);
    let elen = u32::from_le_bytes(elen_b.try_into().unwrap()) as usize;
    let golden = rest[..elen].to_vec();

    let mut plain = cipher.to_vec();
    XChaCha20::new(key.into(), iv.into()).apply_keystream(&mut plain);

    let mut bc = Vec::new();
    lzma_rs::lzma_decompress(&mut plain.as_slice(), &mut bc).unwrap();
    (bc, golden)
}

fn main() {
    let user_flag = std::env::args().nth(1).unwrap_or_default();
    let (bytecode, golden) = decrypt();

    let lua   = Lua::new();
    let nvm: Function = lua.load(&bytecode).into_function()
                           .unwrap().call(()).unwrap();
    let produced: LuaStr = nvm.call(user_flag).unwrap();

    if produced.as_bytes() == golden.as_slice() {
        println!("correct");
    } else {
        println!("wrong");
    }
}