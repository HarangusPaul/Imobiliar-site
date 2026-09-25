"use client";

import { useEffect, useId, useRef, useState, type DragEvent } from "react";

import { MAX_PHOTOS } from "../model";

import styles from "./ListPropertyForm.module.css";

/**
 * Drag-and-drop or browse. Photos stay in the browser as object URLs; the
 * first one is the cover, and clicking another makes it the cover.
 */

export interface Photo {
  id: string;
  file: File;
  url: string;
}

const ACCEPT = ["image/jpeg", "image/png"];

export function PhotoUpload({
  photos,
  onChange,
}: {
  photos: Photo[];
  onChange: (photos: Photo[]) => void;
}) {
  const inputId = useId();
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [notice, setNotice] = useState("");
  const latest = useRef(photos);
  latest.current = photos;

  // Release object URLs when the form goes away.
  useEffect(() => () => latest.current.forEach((p) => URL.revokeObjectURL(p.url)), []);

  const add = (files: FileList | File[]) => {
    const list = Array.from(files);
    const images = list.filter((f) => ACCEPT.includes(f.type));
    const room = MAX_PHOTOS - photos.length;
    const accepted = images.slice(0, Math.max(0, room));
    const skipped = list.length - accepted.length;
    setNotice(
      skipped > 0
        ? `${skipped} file${skipped === 1 ? "" : "s"} skipped: only JPG or PNG, up to ${MAX_PHOTOS} photos.`
        : "",
    );
    if (!accepted.length) return;
    onChange([
      ...photos,
      ...accepted.map((file) => ({ id: crypto.randomUUID(), file, url: URL.createObjectURL(file) })),
    ]);
  };

  const remove = (id: string) => {
    const photo = photos.find((p) => p.id === id);
    if (photo) URL.revokeObjectURL(photo.url);
    onChange(photos.filter((p) => p.id !== id));
  };

  const makeCover = (id: string) => {
    const photo = photos.find((p) => p.id === id);
    if (photo) onChange([photo, ...photos.filter((p) => p.id !== id)]);
  };

  const onDrop = (event: DragEvent) => {
    event.preventDefault();
    setDragging(false);
    add(event.dataTransfer.files);
  };

  return (
    <>
      <label
        htmlFor={inputId}
        className={`${styles.drop} ${dragging ? styles.dropActive : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
      >
        <span className={styles.dropIcon} aria-hidden="true">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 16V4M12 4l-5 5M12 4l5 5M4 16v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3" />
          </svg>
        </span>
        <span className={styles.dropTitle}>
          Drag photos here or <u>browse</u>
        </span>
        <span className={styles.dropDesc}>JPG or PNG, at least 2000px wide. Up to {MAX_PHOTOS} photos.</span>
        <input
          ref={inputRef}
          id={inputId}
          type="file"
          accept={ACCEPT.join(",")}
          multiple
          className="visually-hidden"
          onChange={(e) => {
            if (e.target.files) add(e.target.files);
            e.target.value = "";
          }}
        />
      </label>

      {notice ? <p className={styles.notice}>{notice}</p> : null}

      {photos.length ? (
        <ul className={styles.thumbs} aria-label="Selected photos">
          {photos.map((photo, index) => (
            <li key={photo.id} className={styles.thumb}>
              {/* eslint-disable-next-line @next/next/no-img-element -- local object URL */}
              <img src={photo.url} alt={`Photo ${index + 1}: ${photo.file.name}`} className={styles.thumbImg} />
              {index === 0 ? (
                <span className={styles.cover}>Cover</span>
              ) : (
                <button type="button" className={styles.makeCover} onClick={() => makeCover(photo.id)}>
                  Make cover
                </button>
              )}
              <button
                type="button"
                className={styles.removePhoto}
                onClick={() => remove(photo.id)}
                aria-label={`Remove photo ${index + 1}`}
              >
                ×
              </button>
            </li>
          ))}
          {photos.length < MAX_PHOTOS ? (
            <li>
              <button
                type="button"
                className={`${styles.thumb} ${styles.thumbAdd}`}
                onClick={() => inputRef.current?.click()}
                aria-label="Add more photos"
              >
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true">
                  <path d="M12 5v14M5 12h14" />
                </svg>
              </button>
            </li>
          ) : null}
        </ul>
      ) : null}
    </>
  );
}
