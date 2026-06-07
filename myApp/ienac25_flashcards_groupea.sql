-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : ven. 08 mai 2026 à 22:31
-- Version du serveur : 10.4.32-MariaDB
-- Version de PHP : 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `ienac_flashcards_groupea`
--

-- --------------------------------------------------------

--
-- Structure de la table `boite`
--
CREATE DATABASE IF NOT EXISTS `ienac25_flashcards_groupea`;
USE `ienac25_flashcards_groupea`;
CREATE TABLE `boite` (
  `idboite` int(11) NOT NULL,
  `duree` int(11) DEFAULT NULL,
  `rang` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `carte`
--

CREATE TABLE `carte` (
  `idcarte` int(11) NOT NULL,
  `idpaquet` int(11) DEFAULT NULL,
  `question` text DEFAULT NULL,
  `reponse` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `categorie`
--

CREATE TABLE `categorie` (
  `idcategorie` int(11) NOT NULL,
  `nomcategorie` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `paquet`
--

CREATE TABLE `paquet` (
  `idpaquet` int(11) NOT NULL,
  `datecreation` date DEFAULT NULL,
  `idcreateur` int(11) DEFAULT NULL,
  `idcategorie` int(11) DEFAULT NULL,
  `nompaquet` varchar(50) DEFAULT NULL,
  `public` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `revision`
--

CREATE TABLE `revision` (
  `idutilisateur` int(11) NOT NULL,
  `idcarte` int(11) NOT NULL,
  `idboite` int(11) DEFAULT NULL,
  `date_derniere_revision` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `utilisateur`
--

CREATE TABLE `utilisateur` (
  `idutilisateur` int(11) NOT NULL,
  `pseudo` varchar(50) DEFAULT NULL,
  `mail` varchar(50) DEFAULT NULL,
  `mdp` varchar(400) DEFAULT NULL,
  `nom` varchar(50) DEFAULT NULL,
  `prenom` varchar(50) DEFAULT NULL,
  `statut` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `boite`
--
ALTER TABLE `boite`
  ADD PRIMARY KEY (`idboite`);

--
-- Index pour la table `carte`
--
ALTER TABLE `carte`
  ADD PRIMARY KEY (`idcarte`),
  ADD KEY `idpaquet` (`idpaquet`);

--
-- Index pour la table `categorie`
--
ALTER TABLE `categorie`
  ADD PRIMARY KEY (`idcategorie`),
  ADD UNIQUE KEY `nomcategorie` (`nomcategorie`);

--
-- Index pour la table `paquet`
--
ALTER TABLE `paquet`
  ADD PRIMARY KEY (`idpaquet`),
  ADD KEY `idcreateur` (`idcreateur`),
  ADD KEY `idcategorie` (`idcategorie`);

--
-- Index pour la table `revision`
--
ALTER TABLE `revision`
  ADD PRIMARY KEY (`idutilisateur`,`idcarte`),
  ADD UNIQUE KEY `idcarte_2` (`idcarte`),
  ADD UNIQUE KEY `idutilisateur` (`idutilisateur`),
  ADD KEY `idcarte` (`idcarte`),
  ADD KEY `idboite` (`idboite`);

--
-- Index pour la table `utilisateur`
--
ALTER TABLE `utilisateur`
  ADD PRIMARY KEY (`idutilisateur`),
  ADD UNIQUE KEY `mail` (`mail`),
  ADD UNIQUE KEY `pseudo` (`pseudo`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `boite`
--
ALTER TABLE `boite`
  MODIFY `idboite` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `carte`
--
ALTER TABLE `carte`
  MODIFY `idcarte` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `categorie`
--
ALTER TABLE `categorie`
  MODIFY `idcategorie` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `paquet`
--
ALTER TABLE `paquet`
  MODIFY `idpaquet` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `utilisateur`
--
ALTER TABLE `utilisateur`
  MODIFY `idutilisateur` int(11) NOT NULL AUTO_INCREMENT;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `carte`
--
ALTER TABLE `carte`
  ADD CONSTRAINT `carte_ibfk_1` FOREIGN KEY (`idpaquet`) REFERENCES `paquet` (`idpaquet`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Contraintes pour la table `paquet`
--
ALTER TABLE `paquet`
  ADD CONSTRAINT `paquet_ibfk_1` FOREIGN KEY (`idcreateur`) REFERENCES `utilisateur` (`idutilisateur`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `paquet_ibfk_2` FOREIGN KEY (`idcategorie`) REFERENCES `categorie` (`idcategorie`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Contraintes pour la table `revision`
--
ALTER TABLE `revision`
  ADD CONSTRAINT `revision_ibfk_1` FOREIGN KEY (`idutilisateur`) REFERENCES `utilisateur` (`idutilisateur`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `revision_ibfk_2` FOREIGN KEY (`idcarte`) REFERENCES `carte` (`idcarte`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `revision_ibfk_3` FOREIGN KEY (`idboite`) REFERENCES `boite` (`idboite`) ON DELETE SET NULL ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
