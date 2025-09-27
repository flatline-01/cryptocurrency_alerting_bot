--
-- PostgreSQL database dump
--

\restrict rjUUdsCqe2Mez0XNaZuOvKcsDxYgZu3F2k2UVcM9ny243PfbbRD7dasgkqDoSTI

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: price_movement_direction; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.price_movement_direction AS ENUM (
    'above',
    'below'
);


ALTER TYPE public.price_movement_direction OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alerts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alerts (
    id integer NOT NULL,
    currency_abbr character varying(10) NOT NULL,
    price real NOT NULL,
    user_id bigint NOT NULL,
    delay integer NOT NULL,
    option public.price_movement_direction NOT NULL
);


ALTER TABLE public.alerts OWNER TO postgres;

--
-- Name: alerts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.alerts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.alerts_id_seq OWNER TO postgres;

--
-- Name: alerts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.alerts_id_seq OWNED BY public.alerts.id;


--
-- Name: tg_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tg_users (
    tg_id bigint NOT NULL
);


ALTER TABLE public.tg_users OWNER TO postgres;

--
-- Name: tg_users_tg_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tg_users_tg_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tg_users_tg_id_seq OWNER TO postgres;

--
-- Name: tg_users_tg_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tg_users_tg_id_seq OWNED BY public.tg_users.tg_id;


--
-- Name: alerts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alerts ALTER COLUMN id SET DEFAULT nextval('public.alerts_id_seq'::regclass);


--
-- Name: tg_users tg_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tg_users ALTER COLUMN tg_id SET DEFAULT nextval('public.tg_users_tg_id_seq'::regclass);


--
-- Data for Name: alerts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alerts (id, currency_abbr, price, user_id, delay, option) FROM stdin;
4	ETH	4.487	7322232471	10	above
\.


--
-- Data for Name: tg_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tg_users (tg_id) FROM stdin;
7322232471
\.


--
-- Name: alerts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.alerts_id_seq', 4, true);


--
-- Name: tg_users_tg_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tg_users_tg_id_seq', 1, false);


--
-- Name: alerts alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT alerts_pkey PRIMARY KEY (id);


--
-- Name: tg_users tg_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tg_users
    ADD CONSTRAINT tg_users_pkey PRIMARY KEY (tg_id);


--
-- Name: alerts fk_alerts_tg_users; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT fk_alerts_tg_users FOREIGN KEY (user_id) REFERENCES public.tg_users(tg_id);


--
-- PostgreSQL database dump complete
--

\unrestrict rjUUdsCqe2Mez0XNaZuOvKcsDxYgZu3F2k2UVcM9ny243PfbbRD7dasgkqDoSTI

